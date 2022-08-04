{
    // TODO: replace notification email address with cleopatra@asos.com post testing
    "default": {
        "jobs": [
            {
                "name": "promotheus-preprocess",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS15_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV'),
                        "DATABRICKS_HOST": std.extVar('DATABRICKS_HOST'),
                        "DATABRICKS_TOKEN": std.extVar('DATABRICKS_TOKEN')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_success": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_failure": [
                        "anders.blankholm@asos.com"
                    ]
                },
                // "schedule": {
                //     "quartz_cron_expression": "0 0 13 1/1 * ? *",
                //     "timezone_id": "Europe/London"
                // },
                "max_retries": 1,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "pipeline/run_preprocessing.py",
                    "parameters": [
                        "--first_week_start_date", "20181015",
                        "--last_week_start_date", "20210906",
                        "--serve", "false"
                    ]
                }
            },
            {
                "name": "promotheus-train",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS15_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV'),
                        "DATABRICKS_HOST": std.extVar('DATABRICKS_HOST'),
                        "DATABRICKS_TOKEN": std.extVar('DATABRICKS_TOKEN')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_success": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_failure": [
                        "anders.blankholm@asos.com"
                    ]
                },
                // "schedule": {
                //     "quartz_cron_expression": "0 0 14 1/1 * ? *",
                //     "timezone_id": "Europe/London"
                // },
                "max_retries": 1,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "pipeline/run_train.py",
                    "parameters": [
                        "--end_date", "20180101",
                        "--model_usage", "serve",
                        "--n_estimators", "5",
                        "--n_weeks_data_training", "5",
                        "--tracking_uri", "databricks"
                    ]
                }
            },
            {
                "name": "promotheus-optimise_forecast",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS15_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV'),
                        "DATABRICKS_HOST": std.extVar('DATABRICKS_HOST'),
                        "DATABRICKS_TOKEN": std.extVar('DATABRICKS_TOKEN')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_success": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_failure": [
                        "anders.blankholm@asos.com"
                    ]
                },
                "max_retries": 0,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "pipeline/run_forecast_optimize.py",
                    "parameters": [
                        "--recommend_for_date", "20220124",
                        "--model_run_id", "c854485367d64f919d8dfcfd9ddfb790",
                        "--minutes_in_promo", "10080"
                    ]
                }
            },
            {
                "name": "promotheus-ithaxinate",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS15_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV'),
                        "DATABRICKS_HOST": std.extVar('DATABRICKS_HOST'),
                        "DATABRICKS_TOKEN": std.extVar('DATABRICKS_TOKEN')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_success": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_failure": [
                        "anders.blankholm@asos.com"
                    ]
                },
                "max_retries": 0,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "pipeline/run_ithax.py",
                    "parameters": [
                        "--recommend_for_date", "20180101"
                    ]
                }
            },
            {
                "name": "promotheus-serve",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS15_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV'),
                        "DATABRICKS_HOST": std.extVar('DATABRICKS_HOST'),
                        "DATABRICKS_TOKEN": std.extVar('DATABRICKS_TOKEN')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_success": [
                        "anders.blankholm@asos.com"
                    ],
                    "on_failure": [
                        "anders.blankholm@asos.com"
                    ]
                },
                "max_retries": 0,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "pipeline/run_serve_recommendations.py",
                    "parameters": [
                        "--recommend_for_date", "20180101"
                    ]
                }
            },
            {
                "name": "promotheus-test",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS15_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
		            "spark_env_vars": {
			            "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "DATABRICKS_HOST": std.extVar('DATABRICKS_HOST'),
                        "DATABRICKS_TOKEN": std.extVar('DATABRICKS_TOKEN'),
                        "PROMOTHEUS_ENV": "dev"
                    }
                },
                "timeout_seconds": 4200,
                "max_retries": 0,
                "max_concurrent_runs": 50,
                "spark_python_task": {
                    "python_file": "tests/integration/remote_suite.py",
                    "parameters": []
                }
            },
            {
                "name": "promotheus-stakeholder-metrics",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS12_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "michael.neely@asos.com"
                    ],
                    "on_success": [
                        "michael.neely@asos.com"
                    ],
                    "on_failure": [
                        "michael.neely@asos.com"
                    ]
                },
                "max_retries": 0,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "promotheus/monitoring/run_stakeholder_metrics.py",
                    "parameters": [
                        "--promo_date", "20220502"
                    ]
                }
            },
            {
                "name": "promotheus-populate-predictions",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS12_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "michael.neely@asos.com"
                    ],
                    "on_success": [
                        "michael.neely@asos.com"
                    ],
                    "on_failure": [
                        "michael.neely@asos.com"
                    ]
                },
                "max_retries": 0,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "promotheus/monitoring/run_populate_predictions.py",
                    "parameters": [
                        "--first_date", "20220328",
                        "--last_date", "20220403"
                    ]
                }
            },
            {
                "name": "promotheus-compute-metrics",
                "new_cluster": {
                    "spark_version": "10.1.x-cpu-ml-scala2.12",
                    "node_type_id": "Standard_DS13_v2",
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                        "spark.databricks.clusterUsageTags.clusterNoDriverDaemon": "true"
                    },
                    "custom_tags": {
                        "ResourceClass": "SingleNode"
                    },
                    "num_workers": 0,
                    "spark_env_vars": {
                        "PIP_EXTRA_INDEX_URL": std.extVar('PIP_EXTRA_INDEX_URL'),
                        "ASOS_AI_RETSCI_KEY": std.extVar('ASOS_AI_RETSCI_KEY'),
                        "PROMOTHEUS_ENV": std.extVar('PROMOTHEUS_ENV')
                    }
                },
                "libraries": [],
                "email_notifications": {
                    "on_start": [
                        "michael.neely@asos.com"
                    ],
                    "on_success": [
                        "michael.neely@asos.com"
                    ],
                    "on_failure": [
                        "michael.neely@asos.com"
                    ]
                },
                "max_retries": 0,
                "max_concurrent_runs": 20,
                "spark_python_task": {
                    "python_file": "promotheus/monitoring/run_compute_metrics.py",
                    "parameters": [
                        "--first_date", "20220328",
                        "--last_date", "20220328"
                    ]
                }
            }
        ]
    }
}
