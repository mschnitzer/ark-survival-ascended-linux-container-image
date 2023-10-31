.PHONY: prepare build load

prepare:
	- sudo rm -rf build-results
	- mkdir -p build-results

build: prepare
	- sudo kiwi-ng --color-output --debug system build --target-dir build-results/ --description .
	- sudo xz --threads 4 -z build-results/*.tar

load:
	- sudo docker load -i build-results/*.xz
