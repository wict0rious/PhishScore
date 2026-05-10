"""Expert consensus phishing susceptibility model.

Encodes practitioner survey rankings into a (department, industry) -> risk
score and a set of pretext, persona, OSINT, timing recommendations.
"""
import numpy as np
import pandas as pd
import joblib
from phishscore.config import (
    DEPARTMENT_BLEND_MAP, INDUSTRY_BLEND_MAP, CONTEXT_MODIFIERS,
    DEPARTMENT_ARCHETYPE, ARCHETYPE_BOOSTS, MODIFIER_BOOSTS,
)
from phishscore.survey_analysis import compute_all_weights, run_full_analysis


INDUSTRY_RISK_MODIFIERS = {
    "Financial services": 0.05,
    "Healthcare": 0.08,
    "Government": 0.03,
    "Education": 0.10,
    "Tech companies": -0.05,
    "Law firms": 0.06,
    "Fortune 1,000": 0.02,
    "NGOs": 0.07,
    "Other": 0.0,
}


class PhishingRiskModel:
    """Scoring engine fitted from aggregated survey weights, not labeled
    examples. Calling :meth:`fit` precomputes the per-question weight tables
    used by :meth:`predict`."""

    def __init__(self):
        self.weights = None
        self.full_analysis = None
        self.n_respondents = 0
        self.is_fitted = False

    def fit(self, df):
        self.weights = compute_all_weights(df)
        self.full_analysis = run_full_analysis(df)
        self.n_respondents = len(df)
        self.is_fitted = True
        return self

    def _surveyed_departments(self):
        return self.weights["department_risk"]["department"].tolist()

    def _get_department_risk(self, department):
        dept_df = self.weights["department_risk"]
        match = dept_df[dept_df["department"].str.lower() == department.lower()]
        if len(match) > 0:
            return float(match.iloc[0]["net_risk_score"])
        return 0.0

    def _get_blended_department_risk(self, department):
        """Empirical score if the department was surveyed; otherwise a
        weighted blend of surveyed scores plus an extra offset."""
        direct = self._get_department_risk(department)
        if direct != 0.0 or department.lower() in [
            d.lower() for d in self._surveyed_departments()
        ]:
            return direct, None

        blend_entry = DEPARTMENT_BLEND_MAP.get(department)
        if blend_entry is None:
            return 0.0, None

        score = sum(
            self._get_department_risk(src_dept) * w
            for src_dept, w in blend_entry["blend"].items()
        )
        score += blend_entry.get("extra_offset", 0.0)
        return score, blend_entry["source"]

    def _industry_weight(self):
        norms = self.weights["industry_norms"]["industry_norms"]
        tailored = norms[norms["code"] == 1]
        sometimes = norms[norms["code"] == 2]
        tailored_pct = float(tailored["pct"].iloc[0]) if len(tailored) else 0
        sometimes_pct = float(sometimes["pct"].iloc[0]) if len(sometimes) else 0
        return (tailored_pct + 0.5 * sometimes_pct) / 100.0

    def _get_industry_modifier(self, industry):
        base = INDUSTRY_RISK_MODIFIERS.get(industry, 0.0)
        return base * (1 + self._industry_weight())

    def _get_blended_industry_modifier(self, industry):
        if industry in INDUSTRY_RISK_MODIFIERS:
            return self._get_industry_modifier(industry), None

        blend_entry = INDUSTRY_BLEND_MAP.get(industry)
        if blend_entry is None:
            return 0.0, None

        blended = sum(
            INDUSTRY_RISK_MODIFIERS.get(src_industry, 0.0) * w
            for src_industry, w in blend_entry["blend"].items()
        )
        blended *= (1 + self._industry_weight())
        return blended, blend_entry["source"]

    @staticmethod
    def _apply_modifiers(modifier_keys):
        total = 0.0
        active = []
        for key in modifier_keys:
            entry = CONTEXT_MODIFIERS.get(key)
            if entry:
                total += entry["value"]
                active.append({
                    "key": key,
                    "label": entry["label"],
                    "value": entry["value"],
                })
        return total, active

    def _get_nested_df(self, outer_key, inner_key):
        container = self.weights[outer_key]
        if isinstance(container, dict):
            return container[inner_key]
        return container

    @staticmethod
    def _collect_boosts(department, modifier_keys):
        archetype = DEPARTMENT_ARCHETYPE.get(department, "general")
        combined = {cat: dict(items) for cat, items in ARCHETYPE_BOOSTS.get(archetype, {}).items()}

        for key in modifier_keys:
            for cat, items in MODIFIER_BOOSTS.get(key, {}).items():
                combined.setdefault(cat, {})
                for label, factor in items.items():
                    combined[cat][label] = combined[cat].get(label, 1.0) * factor
        return combined

    def _boosted_top_items(self, weight_key, boost_cat, boosts, n=3):
        wdf = self.weights[weight_key].copy()
        score_col = "normalized_score" if "normalized_score" in wdf.columns else "pct"
        cat_boosts = boosts.get(boost_cat, {})
        if cat_boosts:
            wdf["_boosted"] = wdf.apply(
                lambda r: r[score_col] * cat_boosts.get(r["label"], 1.0), axis=1
            )
            wdf = wdf.sort_values("_boosted", ascending=False)
        top = wdf.head(n)
        return list(zip(top["label"].tolist(), top[score_col].tolist()))

    def _boosted_top_nested(self, outer_key, inner_key, boost_cat, boosts, n=5):
        wdf = self._get_nested_df(outer_key, inner_key).copy()
        cat_boosts = boosts.get(boost_cat, {})
        if cat_boosts:
            wdf["_boosted"] = wdf.apply(
                lambda r: r["pct"] * cat_boosts.get(r["label"], 1.0), axis=1
            )
            wdf = wdf.sort_values("_boosted", ascending=False)
        top = wdf.head(n)
        return list(zip(top["label"].tolist(), top["pct"].tolist()))

    def predict(self, name, department, company, industry,
                mode="pure", modifier_keys=None):
        """Return a full assessment dict for the given target.

        ``mode="pure"`` uses only direct survey scores. ``mode="enhanced"``
        adds taxonomy blending and applies any active context modifiers.
        """
        if not self.is_fitted:
            raise RuntimeError("Model has not been fitted. Call .fit(df) first.")

        modifier_keys = modifier_keys or []
        dept_blend_source = None
        industry_blend_source = None

        if mode == "enhanced":
            dept_risk, dept_blend_source = self._get_blended_department_risk(department)
            industry_mod, industry_blend_source = self._get_blended_industry_modifier(industry)
            modifier_total, active_modifiers = self._apply_modifiers(modifier_keys)
        else:
            dept_risk = self._get_department_risk(department)
            industry_mod = self._get_industry_modifier(industry)
            modifier_total = 0.0
            active_modifiers = []

        raw_score = dept_risk + industry_mod + modifier_total
        susceptibility_score = int(np.clip((raw_score + 1) / 2 * 100, 0, 100))

        if susceptibility_score >= 75:
            susceptibility_level = "Critical"
        elif susceptibility_score >= 55:
            susceptibility_level = "High"
        elif susceptibility_score >= 35:
            susceptibility_level = "Medium"
        else:
            susceptibility_level = "Low"

        boosts = self._collect_boosts(department, modifier_keys)

        top_targeting = self._boosted_top_items("targeting_factors", "targeting_factors", boosts, 3)
        top_psych = self._boosted_top_items("psych_levers", "psych_levers", boosts, 5)
        top_credibility = self._boosted_top_items("pretext_credibility", "credibility", boosts, 3)
        top_persona = self._boosted_top_items("persona_crafting", "persona", boosts, 3)
        top_pretext = self._boosted_top_items("pretext_design_factors", "pretext_design", boosts, 5)
        top_send_times = self._boosted_top_nested("timing", "best_send_times", "timing", boosts, 5)
        top_osint = self._boosted_top_nested("osint_sources", "osint_sources", "osint", boosts, 5)
        top_protective = self._boosted_top_items("protective_factors", "protective", boosts, 3)

        dept_df = self.weights["department_risk"]
        dept_rank = None
        for i, row in dept_df.iterrows():
            if row["department"].lower() == department.lower():
                dept_rank = i + 1
                break

        result = {
            "target": {
                "name": name,
                "department": department,
                "company": company,
                "industry": industry,
            },
            "susceptibility_assessment": {
                "susceptibility_score": susceptibility_score,
                "susceptibility_level": susceptibility_level,
                "department_susceptibility_raw": round(dept_risk, 4),
                "industry_modifier": round(industry_mod, 4),
                "modifier_total": round(modifier_total, 4),
                "department_rank": f"{dept_rank}/{len(dept_df)}" if dept_rank else "N/A",
            },
            "attack_recommendations": {
                "targeting_factors": [
                    {"factor": f, "weight": round(w, 4)} for f, w in top_targeting
                ],
                "psychological_levers": [
                    {"lever": l, "weight": round(w, 4)} for l, w in top_psych
                ],
                "pretext_design": [
                    {"factor": f, "selected_by_pct": w} for f, w in top_pretext
                ],
                "optimal_timing": [
                    {"timing": t, "selected_by_pct": w} for t, w in top_send_times
                ],
                "persona_approach": [
                    {"approach": a, "weight": round(w, 4)} for a, w in top_persona
                ],
                "credibility_factors": [
                    {"factor": f, "weight": round(w, 4)} for f, w in top_credibility
                ],
                "osint_sources": [
                    {"source": s, "selected_by_pct": w} for s, w in top_osint
                ],
            },
            "defensive_insights": {
                "protective_factors": [
                    {"factor": f, "selected_by_pct": w} for f, w in top_protective
                ],
                "recommendation": self._generate_defensive_recommendation(
                    department, susceptibility_level, top_protective
                ),
            },
            "reasoning": self._generate_reasoning(
                department, industry, dept_risk, industry_mod,
                susceptibility_score, susceptibility_level, dept_rank, len(dept_df),
            ),
            "model_info": {
                "mode": mode,
                "n_practitioners": self.n_respondents,
                "data_source": "Cybersecurity practitioner survey",
            },
        }

        if mode == "enhanced":
            result["enhanced_info"] = {
                "department_blend_source": dept_blend_source,
                "industry_blend_source": industry_blend_source,
                "active_modifiers": [
                    {"label": m["label"], "value": m["value"]}
                    for m in active_modifiers
                ],
            }

        return result

    def _generate_reasoning(self, department, industry, dept_risk, industry_mod,
                            susceptibility_score, susceptibility_level,
                            dept_rank, total_depts):
        lines = []

        rank_str = f", ranked #{dept_rank} of {total_depts} departments" if dept_rank else ""
        inferred_note = " (inferred from blended survey data)" if dept_rank is None else ""

        if dept_risk > 0.3:
            lines.append(
                f"{department} is classified as HIGHLY susceptible{inferred_note} "
                f"(net susceptibility: {dept_risk:+.2f}{rank_str})."
            )
        elif dept_risk > 0:
            lines.append(
                f"{department} is classified as moderately susceptible{inferred_note} "
                f"(net susceptibility: {dept_risk:+.2f}{rank_str})."
            )
        elif dept_risk < 0:
            lines.append(
                f"{department} is classified as relatively RESISTANT{inferred_note} "
                f"(net susceptibility: {dept_risk:+.2f}{rank_str})."
            )
        else:
            lines.append(
                f"{department} has a neutral susceptibility profile{inferred_note} "
                f"(net susceptibility: {dept_risk:+.2f})."
            )

        if industry_mod > 0:
            lines.append(
                f"The {industry} sector adds a slight positive modifier ({industry_mod:+.4f})."
            )
        elif industry_mod < 0:
            lines.append(
                f"The {industry} sector provides a slight protective modifier ({industry_mod:+.4f})."
            )

        lines.append(
            f"Combined susceptibility score: {susceptibility_score}/100 "
            f"({susceptibility_level}). Based on {self.n_respondents} practitioner responses."
        )
        return " ".join(lines)

    def _generate_defensive_recommendation(self, department, susceptibility_level, top_protective):
        recs = []
        if susceptibility_level in ("Critical", "High"):
            recs.append(
                f"PRIORITY: {department} should receive enhanced security awareness "
                f"training with phishing simulations tailored to their role."
            )
            recs.append(
                "Apply stricter email filtering and additional authentication "
                "requirements for sensitive actions."
            )
        elif susceptibility_level == "Medium":
            recs.append(
                f"{department} should receive regular security awareness training "
                f"with periodic phishing simulations."
            )
        else:
            recs.append(
                f"{department} shows lower susceptibility. Maintain standard training cadence."
            )

        if top_protective:
            factors = [f[0] for f in top_protective[:2]]
            recs.append(f"Key protective factors to reinforce: {'; '.join(factors)}.")
        return " ".join(recs)

    def save(self, path):
        joblib.dump({
            "weights": {
                k: v.to_dict() if isinstance(v, pd.DataFrame) else
                {k2: v2.to_dict() if isinstance(v2, pd.DataFrame) else v2
                 for k2, v2 in v.items()}
                for k, v in self.weights.items()
            },
            "n_respondents": self.n_respondents,
            "is_fitted": self.is_fitted,
        }, path)

    @staticmethod
    def _is_nested_dict_of_dfs(v):
        if not isinstance(v, dict):
            return False
        for inner in v.values():
            if isinstance(inner, dict) and any(isinstance(vv, dict) for vv in inner.values()):
                return True
        return False

    @classmethod
    def load(cls, path):
        data = joblib.load(path)
        model = cls()
        weights = {}
        for k, v in data["weights"].items():
            if not isinstance(v, dict):
                weights[k] = v
            elif cls._is_nested_dict_of_dfs(v):
                inner = {}
                for k2, v2 in v.items():
                    if isinstance(v2, dict):
                        try:
                            inner[k2] = pd.DataFrame(v2)
                        except (ValueError, TypeError):
                            inner[k2] = v2
                    else:
                        inner[k2] = v2
                weights[k] = inner
            else:
                try:
                    weights[k] = pd.DataFrame(v)
                except (ValueError, TypeError):
                    weights[k] = v
        model.weights = weights
        model.n_respondents = data["n_respondents"]
        model.is_fitted = data["is_fitted"]
        return model
