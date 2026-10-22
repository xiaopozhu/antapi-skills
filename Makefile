PYTHON ?= python3
SKILLS_REF ?= skills-ref

.PHONY: check check-release test validate verify

check:
	$(PYTHON) scripts/check_structure.py

check-release: verify
	$(PYTHON) scripts/check_structure.py --require-skills

test:
	$(PYTHON) -m unittest discover -s scripts -v

validate:
	$(PYTHON) scripts/validate_skills.py --validator "$(SKILLS_REF)"

verify: check test validate
