mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

.PHONY: help
help:                           ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: install-tensor-package
install-tensor-package:         ## install rust_paillier.
	@echo "install rust_paillier"
	@maturin develop --release -m rust/tensor/rust_paillier/Cargo.toml 

.PHONY: build-tensor-package
build-tensor-package:           ## build rust_paillier.
	@echo "build rust_paillier"
	@maturin build --release -m rust/tensor/rust_paillier/Cargo.toml

.PHONY: clean
clean:                          ## Clean unused files.
	@find ./python/ -name '*.pyc' -exec rm -f {} \;
	@find ./python/ -name '__pycache__' -exec rm -rf {} \;

.PHONY: proto-gen-osx
proto-gen-osx:                  ## generate osx protobuf.
	@python3 -m grpc_tools.protoc --proto_path=proto/ \
		--python_out=python/fate/arch/federation/osx/ \
		--grpc_python_out=python/fate/arch/federation/osx/ \
		proto/osx.proto