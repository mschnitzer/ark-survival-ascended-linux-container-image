.PHONY: prepare build build-development build-beta load

prepare:
	- sudo rm -rf build-results
	- mkdir -p build-results

build: prepare
	- sudo kiwi-ng --profile stable --color-output --debug system build --target-dir build-results/ --description .
	- sudo xz --threads 4 -z build-results/*.tar

build-development: prepare
	- sudo kiwi-ng --profile development --color-output --debug system build --target-dir build-results/ --description .
	- sudo xz --threads 4 -z build-results/*.tar

build-beta: prepare
	- sudo kiwi-ng --profile beta --color-output --debug system build --target-dir build-results/ --description .
	- sudo xz --threads 4 -z build-results/*.tar

load:
	- sudo docker load -i build-results/*.xz
