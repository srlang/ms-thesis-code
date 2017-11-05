.PHONY: test_train test_rest

test_files = test_agent.py test_analyze.py test_cribbage__game.py test_cribbage__scoring.py test_records.py test_strategy.py test_strategy2.py test_strategy3.py test_weights.py

test_all: test_smart test_train test_rest

test_train:
	test -f checkpoints/checkpoint_TestAgent_TestStartTime_100.txt && \
		rm -v checkpoints/checkpoint_TestAgent_TestStartTime_100.txt
	test -d checkpoints_dne && rm -rv checkpoints_dne
	py.test -v test_train.py

test_smart:
	py.test -v test_agent_smart.py

test_rest:
	py.test -v $(test_files)
