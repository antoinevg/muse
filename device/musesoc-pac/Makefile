SVD := ../../build/gensvd/musesoc.svd

svd2rust:
	rm -rf build src/generated.rs src/generated/
	mkdir build

	cp $(SVD) svd/musesoc.svd
	svd2rust -i svd/musesoc.svd -o build/ --target riscv --const_generic --make_mod
	mv build/mod.rs src/generated.rs
	mv build/build.rs .
	mv build/device.x .

	form -i src/generated.rs -o src/generated/
	mv src/generated/lib.rs src/generated.rs
	cargo fmt -- --emit files

doc:
	cargo doc --no-deps --all-features --document-private-items --open

distclean:
	rm -rf build/ target/ src/generated.rs src/generated/ svd/musesoc.svd
