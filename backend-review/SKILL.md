---
name: backend-review
description: Extension module for reviewing backend systems, APIs, distributed systems, services, workers, queues, or infrastructure-heavy applications. Prioritizes correctness, operational simplicity, and reliability under failure.
---

# Backend System Extensions

When reviewing backend systems, APIs, distributed systems, services, workers, queues, or infrastructure-heavy applications, additionally perform the following deep analysis.

Backend review must prioritize:
- correctness
- operational simplicity
- reliability under failure
- debuggability
- scalability realism
- latency consistency
- maintainability over abstraction

Do NOT reward:
- unnecessary microservices
- excessive async/event systems
- framework-heavy architecture
- over-engineered domain abstractions
- speculative scalability

## 1. API DESIGN & CONTRACTS

Review:
- API consistency
- schema quality
- versioning strategy
- pagination design
- idempotency guarantees
- backward compatibility
- error semantics
- serialization format
- RPC vs REST appropriateness
- contract evolution safety

Find:
- inconsistent APIs
- leaky abstractions
- unstable response contracts
- weak validation
- ambiguous semantics
- hidden breaking changes
- over-chatty APIs
- poor batching strategy
- bad pagination patterns
- unsafe assumptions

Evaluate:
- whether APIs are maintainable long term
- whether contracts are operationally safe

## 2. DATABASE DESIGN

Review:
- schema design
- indexing strategy
- normalization tradeoffs
- query patterns
- migration safety
- transactional boundaries
- write amplification
- read amplification
- consistency guarantees
- locking/contention risks

Find:
- N+1 queries
- missing indexes
- over-normalization
- dangerous migrations
- weak transactional assumptions
- contention hotspots
- poor query design
- hidden scalability cliffs
- data duplication without justification

Evaluate:
- what breaks first at scale
- operational DB risks
- migration survivability

Explicitly identify:
- queries likely to become bottlenecks
- tables likely to become hotspots
- dangerous growth assumptions

## 3. CONCURRENCY & DISTRIBUTED SYSTEMS

Review:
- concurrency model
- synchronization patterns
- async execution
- worker coordination
- queue semantics
- retry behavior
- event ordering assumptions
- distributed locking
- consistency handling

Find:
- race conditions
- deadlocks
- retry storms
- duplicate processing
- event ordering bugs
- unsafe concurrency assumptions
- distributed monolith behavior
- hidden coupling through events

Evaluate:
- whether concurrency complexity is justified
- whether distributed assumptions are realistic

Identify:
- failure amplification risks
- cascading retry risks
- queue buildup scenarios

## 4. RELIABILITY ENGINEERING

Review:
- timeout strategy
- retry policy
- circuit breakers
- fallback behavior
- degradation modes
- recovery paths
- deployment safety
- health checks
- failover handling

Find:
- retry explosions
- infinite retries
- timeout mismatches
- hidden dependency chains
- brittle recovery logic
- silent data corruption risks
- inconsistent failure handling
- unsafe shutdown behavior

Evaluate:
- production survivability
- incident blast radius
- operational recovery difficulty

## 5. PERFORMANCE & LATENCY

Review:
- p50/p95/p99 assumptions
- IO patterns
- network overhead
- serialization costs
- connection pooling
- cache behavior
- query latency
- hot paths
- worker throughput

Find:
- blocking IO
- connection exhaustion
- excessive serialization
- poor batching
- unnecessary DB roundtrips
- memory pressure
- cache stampedes
- expensive synchronous chains

Evaluate:
- latency consistency under load
- tail latency risks
- operational cost scaling

Ignore:
- meaningless microbenchmarks
- premature optimization

## 6. CACHING STRATEGY

Review:
- cache invalidation
- TTL assumptions
- consistency tradeoffs
- cache ownership
- cache warming
- stale-read tolerance

Find:
- invalid cache assumptions
- stale data risks
- cache poisoning risks
- duplicated caches
- cache stampedes
- missing invalidation logic
- over-caching

Evaluate:
- whether caching complexity is justified
- operational cache risks

## 7. MESSAGE QUEUES & EVENT SYSTEMS

Review:
- event contracts
- delivery guarantees
- idempotency
- dead-letter handling
- replay behavior
- consumer isolation
- ordering guarantees

Find:
- poison message risks
- replay corruption risks
- event schema drift
- consumer coupling
- unbounded retries
- hidden orchestration complexity

Evaluate:
- whether events simplify or complicate the system
- whether async boundaries are justified

Be skeptical of:
- event-driven architecture without scale justification
- async systems replacing simple synchronous flows

## 8. OBSERVABILITY & INCIDENT RESPONSE

Review:
- structured logging
- tracing
- metrics quality
- alerting usefulness
- debugging ergonomics
- correlation IDs
- audit trails

Find:
- logging noise
- missing operational visibility
- impossible-to-debug flows
- hidden failure paths
- poor traceability

Evaluate:
- how difficult production incidents would be
- mean-time-to-diagnosis realism

## 9. SECURITY & TRUST BOUNDARIES

Review:
- auth/authz enforcement
- trust boundaries
- secrets management
- rate limiting
- abuse prevention
- SSRF exposure
- deserialization risks
- tenant isolation

Find:
- privilege escalation paths
- missing authorization checks
- weak isolation
- dangerous internal trust assumptions
- insecure defaults
- unsafe admin flows

Evaluate:
- attack surface realism
- production abuse survivability

## 10. INFRASTRUCTURE & DEPLOYMENT

Review:
- deployment model
- rollback safety
- infra complexity
- containerization quality
- CI/CD reliability
- environment consistency
- config management

Find:
- deployment fragility
- environment drift
- unsafe migrations
- snowflake infrastructure
- manual operational dependencies
- hidden infra coupling

Evaluate:
- operational burden
- deploy confidence
- rollback survivability

## 11. BACKEND SIMPLICITY AUDIT (CRITICAL)

Aggressively identify:
- unnecessary services
- fake scalability
- premature microservices
- excessive event systems
- abstraction layers without ROI
- repositories/services/factories that add no value
- framework-driven architecture
- orchestration complexity
- over-generic infrastructure

Explicitly answer:
- What should be merged?
- What should become synchronous?
- What should be deleted?
- What complexity is unjustified?
- What abstractions are pretending to help?
- Which services should not exist?

This section is mandatory.

# BACKEND FINAL ASSESSMENT

Explicitly answer:

- Is the backend operationally sane?
- Is the architecture justified by actual scale?
- What fails first under load?
- What causes the next production incident?
- Is the infra complexity earned?
- Is this maintainable by an average engineering team?
- Does this system optimize for engineering ego or reliability?