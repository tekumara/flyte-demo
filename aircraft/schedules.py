from flytekit import CronSchedule, LaunchPlan
from flytekit.core.workflow import ReferenceWorkflow

aircraft_etl_flow_main = ReferenceWorkflow(
    project="flyteexamples",
    domain="development",
    name="aircraft.etl_flow.main",
    version="v1",
    inputs={},
    outputs={},
)

# creates a launch plan that runs at 10am UTC every day.
aircraft_daily = LaunchPlan.get_or_create(
    name="aircraft_daily",
    workflow=aircraft_etl_flow_main,
    # Cron expression strings use the `AWS syntax <http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions>`_.
    schedule=CronSchedule(cron_expression="0 10 * * ? *"),
)
