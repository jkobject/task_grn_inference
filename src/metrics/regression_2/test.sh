viash build src/metrics/regression_2/config.vsh.yaml -p docker -o bin/regression_2 && bin/regression_2/regression_2 --perturbation_data resources/grn-benchmark/perturbation_data.h5ad --tfs resources/grn_benchmark/prior/tf_all.csv --consensus resources/grn_benchmark/prior/consensus-num-regulators.json --layer scgen_pearson --reg_type ridge --prediction resources/grn-benchmark/grn_models/scenicplus.csv