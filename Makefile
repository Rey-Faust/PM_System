.PHONY: init cockpit digest weekly-pack reset

init:
	./scripts/init_workspace.sh

cockpit:
	python3 scripts/build_cockpit.py

digest:
	python3 scripts/build_weekly_digest.py

weekly-pack: cockpit digest

reset:
	rm -f data/*.csv
	./scripts/init_workspace.sh
