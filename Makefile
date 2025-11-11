.PHONY: prepare build build-development build-beta load

GLOBAL_BUILD_DIR = /tmp/.kiwi-build-results
TARGET_DIR = $(GLOBAL_BUILD_DIR)/ark-survival-ascended-linux-container-image

prepare:
	- sudo rm -rf $(TARGET_DIR)
	- mkdir -p $(GLOBAL_BUILD_DIR)

build: prepare
	- sudo kiwi-ng --profile stable --color-output --debug system build --target-dir $(TARGET_DIR) --description .

build-development: prepare
	- sudo kiwi-ng --profile development --color-output --debug system build --target-dir $(TARGET_DIR) --description .

build-beta: prepare
	- sudo kiwi-ng --profile beta --color-output --debug system build --target-dir $(TARGET_DIR) --description .

load:
	- sudo docker load -i $(TARGET_DIR)/*.xz
