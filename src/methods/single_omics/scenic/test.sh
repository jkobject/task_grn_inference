viash run src/methods/single_omics/scenic/config.vsh.yaml -- \
    --multiomics_rna resources_test/grn-benchmark/multiomics_rna.h5ad \
    --tf_all resources/grn_benchmark/prior/tf_all.csv \
    --prediction output/scenic_prediction.csv \
    --temp_dir output/scenic