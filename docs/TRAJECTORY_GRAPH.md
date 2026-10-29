# Trajectory audit graph

FrontierLab maintains two different graphs for two different questions.

## Evidence graph

The evidence graph asks:

> Can this scientific artifact be traced back to checked source material?

It is used by the EXTRACTED-only plan-step gate.

## Trajectory audit graph

The trajectory graph asks:

> What happened during this research run?

It records process events that should be auditable but must not be mistaken for scientific evidence.

The schema is:

```text
frontierlab.trajectory-graph.v1
```

It contains a fixed five-stage workflow spine plus optional audit nodes for:

- model-call receipts;
- normalized human-intervention events;
- saved method evaluation;
- rejected claims;
- deterministic process-taxonomy signals.

## Deliberate separation from the evidence gate

Trajectory nodes never participate in `step_gate()`.

A failed model call, a researcher approval or a rejected claim can be important for process auditing, but none of those facts makes a scientific claim more true.

The trajectory graph therefore has its own relations such as:

- `NEXT_STAGE`
- `EXECUTED_IN`
- `INTERVENED_IN`
- `RECORDED_IN`
- `REJECTED_IN`
- `SIGNALED_IN`

These are process relations, not evidence-provenance tags.

## Privacy / provenance boundary

Model-call nodes use receipt metadata only:

- role;
- requested/reported model;
- status;
- start time;
- input/output SHA-256;
- finish reason;
- token usage;
- elapsed seconds.

Prompts and model outputs are not copied into the trajectory graph.

Human-event nodes preserve the actor label and `identity_verified` flag already present in the intervention event. FrontierLab does not claim cryptographic identity verification.

## Export

`frontierlab.reporting.export_json(run)` includes both:

```json
{
  "process_metrics": {...},
  "trajectory_graph": {...}
}
```

The Streamlit interface also exposes a dedicated **Trajectory audit graph · process trace** panel and a `trajectory.json` download.

## Scientific boundary

The trajectory graph is an audit record. It does not measure model accuracy, prove scientific entailment, authorize a plan step or validate an experiment.
