.PHONY: test_train

test_train:
	test -f checkpoints/checkpoint_TestAgent_TestStartTime_100.txt && \
		rm -v checkpoints/checkpoint_TestAgent_TestStartTime_100.txt
	test -d checkpoints_dne && rm -rv checkpoints_dne
	py.test -v test_train.py
