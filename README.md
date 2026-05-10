# PhishScore

A phishing susceptibility scoring engine powered by expert insights.

Built from a survey of 27 infosec/cybersecurity practitioners with extensive experience in red teaming, social engineering, penetration testing, threat hunting, incident response, and more!

## Quick start

```bash
git clone https://github.com/wict0rious/PhishScore phishscore
cd phishscore
python3 -m venv .ps
. .ps/bin/activate
pip3 install -e .
```

`pip3 install -e .` installs the package in editable mode and puts a `phishscore` executable on your `PATH`. If you'd rather not install, the same CLI is reachable as `python3 -m phishscore`.

Train the model on first run and launch the interactive menu:

```bash
phishscore
```

You can also request a single assessment:

```bash
phishscore \
    --model enhanced \
    --assessment offensive \
    --name "Nick Mullen" \
    --department "Cybersecurity/InfoSec" \
    --company "CT Corp" \
    --industry "Tech companies" \
    --modifiers "technical,remote"
```

Useful flags:

| Flag | Description |
| --- | --- |
| `--model {pure,enhanced}` | `pure` uses only the survey scores, `enhanced` adds taxonomy blending and context modifiers |
| `--assessment {default,offensive,defensive}` | Output style, suited for different professional perspectives |
| `--modifiers KEYS` | Comma-separated context modifiers (`technical`, `remote`, `deadline`, etc. |
| `--report` | Also write JSON, TXT and HTML copies into `output/reports/` |
| `--retrain` | Discard any cached model and retrain from the CSVs |

## How it works

For a given target the model:

1. Looks up the empirical net susceptibility of the target's department from the data. For non-surveyed departments it computes a weighted blend of surveyed ones, plus an optional offset (e.g. a `Cybersecurity/InfoSec` role inherits `IT helpdesk`'s base score and then receives a strong protective offset).
2. Applies an industry modifier and any active context modifiers (`technical`, `remote`, `deadline`, `leadership`, etc.).
3. Re-ranks the global survey recommendations (psychological levers, pretext design factors, OSINT sources, optimal timing, persona approach, credibility factors, protective controls) using archetype and modifier-specific boost factors so that the output is tailored to the target rather than identical for every query.

The final 0-100 score is interpreted as **relative susceptibility within typical organizational roles**, NOT as a per-attempt success probability for a given individual.

The CSVs in `data/` are the public, redacted versions of the original Qualtrics export. Free-text responses (the `*_TEXT` "Other" fields and the open-ended questions Q21-Q23) and Qualtrics metadata such as timestamps, distribution channel, user language, and the consent block have been stripped. Response IDs have been replaced with sequential anonymous identifiers (`R001`, `R002`, ...).

## Auxiliary scripts

One-off analysis and data validation scripts are in `scripts/`. Run them from the project root, e.g. `python3 scripts/run_analysis.py`. These can be run to get a clean model, or if more responses are collected and need to be analyzed.

## Disclaimers

Human susceptibility is not a fixed quantity. It shifts with cognitive state, emotional condition, workload, personal circumstances, and other factors that change hour to hour. It is **very important** to remember that the output susceptibility score applies to an employee role only. It does not assess a specific individual's character or competence.

These scores should inform role-level training priorities, general policy and process decisions, and resource allocation for security teams. They should **NEVER** be used for judgments about individual employees or punishment. Please reconsider your priorities in life if that is not how you think. 

## Acknowledgements

This work was done for a master's thesis, and made possible with the help of 27 professionals. The full thesis text can be found here: [Understanding Phishing Susceptibility Through Expert Consensus Using Digital Marketing Parallels and a Machine Learning-Based Implementation](https://cornerstone.lib.mnsu.edu/etds/1587/)

## License

MIT. See [LICENSE](LICENSE).
