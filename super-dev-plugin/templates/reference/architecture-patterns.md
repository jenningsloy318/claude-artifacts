---
name: architecture-patterns
description: Software architecture patterns, principles, and best practices for system design. Reference for Phase 5.3 (Architecture Design) in super-dev workflow.
---

# Architecture Patterns Reference

Reference documentation for software architecture design. Use this during Phase 5.3 (Architecture Design) of the super-dev workflow.

## Core Principles

### YAGNI (You Aren't Gonna Need It)
- Design only architecture explicitly required
- No speculative modules or over-engineering
- Each architectural decision must serve documented requirements

### SOLID Principles
- **S**ingle Responsibility - Each module has one reason to change
- **O**pen/Closed - Open for extension, closed for modification
- **L**iskov Substitution - Subtypes must be substitutable
- **I**nterface Segregation - Many specific interfaces over one general
- **D**ependency Inversion - Depend on abstractions, not concretions

### Boring Architecture First
- Prefer proven, familiar patterns over novel approaches
- Standard 3-tier, MVC, or Clean Architecture unless requirements demand otherwise
- Simple > Clever: If a simple solution works, don't add layers

### Key Definitions
- **No Wheel Reinvention**: Prefer reusing mature open-source components over building custom solutions
- **Glue Code**: Minimal integration adapters/layers that connect reused components to existing systems
- **Interface-first Modularity**: Define contracts (interfaces/ports) before implementations

## Decision Framework

### Evaluation Criteria

| Category | Criteria | Description | Weight |
|----------|----------|-------------|--------|
| **Technical Quality** | Modularity | How well-separated are concerns? | 0.10 |
| | Coupling/Cohesion | How loosely coupled/highly cohesive? | 0.10 |
| | Scalability | Growth capacity and scaling strategy | 0.10 |
| | Performance | Response times, throughput, efficiency | 0.10 |
| | Security | Authentication, authorization, data protection | 0.10 |
| **Delivery** | Implementation Complexity | How difficult to implement? | 0.08 |
| | Risk | Technical, schedule, and dependency risks | 0.08 |
| | Time-to-Value | How quickly can we deliver value? | 0.07 |
| | Maintainability | Ease of future changes | 0.04 |
| | Testability | How easy to test? | 0.03 |
| **Operational** | Observability | Logging, metrics, tracing, debugging | 0.05 |
| | Reliability | Uptime, fault tolerance, recovery | 0.05 |
| | Cost | Infrastructure, licensing, operational costs | 0.05 |
| | Supportability | Documentation, community, expertise | 0.03 |
| | Reversibility | How easy to change/rollback? | 0.02 |

**Scoring Rubric:**
- 5 = Excellent (best possible outcome)
- 4 = Good (above average)
- 3 = Acceptable (meets baseline requirements)
- 2 = Fair (below average, may need workarounds)
- 1 = Poor (significant concerns)
- 0 = Unacceptable (cannot be used)

## Architectural Patterns

### Module Decomposition Patterns

#### Domain-Driven Design (DDD)
- **Bounded Contexts**: Define business capability boundaries
- **Aggregates**: Group related entities as consistency boundaries
- **Ubiquitous Language**: Shared language within bounded contexts
- **Context Mapping**: Define relationships between contexts

**When to use:**
- Complex business domains with many rules
- Large teams requiring clear boundaries
- Long-lived projects with evolving requirements

#### Layered Architecture
```
┌─────────────────────────┐
│   Presentation Layer    │  UI, API controllers
├─────────────────────────┤
│    Business Logic       │  Application services, use cases
├─────────────────────────┤
│    Data Access Layer    │  Repositories, DAOs
├─────────────────────────┤
│    Database/External    │  Storage, third-party services
└─────────────────────────┘
```

**When to use:**
- Traditional CRUD applications
- Small to medium teams
- Clear separation of concerns needed

#### Hexagonal/Clean Architecture
```
         ┌──────────────┐
         │   Entities   │  Core business rules
         └──────┬───────┘
                │
         ┌──────┴───────┐
         │  Use Cases   │  Application business rules
         └──────┬───────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───┴───┐  ┌───┴───┐  ┌───┴────┐
│  Web  │  │  DB   │  │  API   │  Adapters/Interfaces
└───────┘  └───────┘  └────────┘
```

**When to use:**
- Complex business logic
- Multiple delivery mechanisms (web, API, CLI)
- Testability is critical

#### Microservices
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Service A│  │ Service B│  │ Service C│  Independent services
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
            ┌──────┴──────┐
            │ API Gateway │
            │ Message Bus │
            └─────────────┘
```

**When to use:**
- Large teams requiring independent deployment
- Different scalability needs per service
- Technology diversity required
**Trade-offs:** Increased operational complexity, distributed transactions

### Data Access Patterns

#### Repository Pattern
```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}
```

**Benefits:**
- Centralized data access logic
- Easy to mock for testing
- Swappable data sources

#### Data Mapper (vs Active Record)
- **Data Mapper**: Separate mapping logic from domain model
- **Active Record**: Model contains data access methods

**Choose Data Mapper when:**
- Complex business logic in domain models
- Need to decouple from database schema
- Multiple data sources for same entity

#### CQRS (Command Query Responsibility Segregation)
```typescript
// Write side (Commands)
interface UserWriteModel {
  create(command: CreateUserCommand): Promise<void>;
  update(command: UpdateUserCommand): Promise<void>;
}

// Read side (Queries)
interface UserReadModel {
  findById(id: string): Promise<UserViewDto>;
  search(query: UserSearchQuery): Promise<UserViewDto[]>;
}
```

**When to use:**
- High read/write ratio workloads
- Complex query requirements
- Eventual consistency acceptable

### Communication Patterns

#### REST API
- Resource-based URLs: `/api/v1/users/{id}`
- HTTP verbs: GET, POST, PUT, PATCH, DELETE
- Stateless communication
**Best for:** Standard CRUD operations, public APIs

#### GraphQL
- Schema-driven: Single endpoint, typed queries
- Clients control data shape
- Introspection and documentation
**Best for:** Complex data requirements, mobile clients

#### gRPC
- Protocol Buffers for efficient serialization
- Strong typing and code generation
- Bidirectional streaming
**Best for:** Microservice communication, high-performance needs

#### Message Queues (RabbitMQ, SQS, Kafka)
- Asynchronous communication
- Event-driven architecture
- Decoupled producers/consumers
**Best for:** Eventual consistency, background processing, fan-out

### State Management Patterns

#### Client-Side State
- **Local Component State**: useState, setState (simple, isolated)
- **Context/Redux**: Global shared state (complex state, many consumers)
- **Server State**: React Query, SWR (caching, synchronization)

#### Server-Side State
- **Session Store**: In-memory, Redis (user session data)
- **Database**: Persistent state (PostgreSQL, MongoDB)
- **Cache Layer**: Redis, Memcached (frequently accessed data)

### Caching Strategies

#### Cache-Aside (Lazy Loading)
```
1. Check cache
2. If miss: load from DB, write to cache, return
3. If hit: return cached data
```

#### Write-Through
```
1. Write to cache
2. Write to DB (synchronous)
3. Return
```

#### Write-Behind (Write-Back)
```
1. Write to cache
2. Return immediately
3. Async write to DB
```

### Error Handling Patterns

#### Circuit Breaker
```typescript
class CircuitBreaker {
  private failures = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';

  async execute(fn: () => Promise): Promise {
    if (this.state === 'OPEN') throw new Error('Circuit open');
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
}
```

#### Retry with Exponential Backoff
```typescript
async function retryWithBackoff(
  fn: () => Promise,
  maxAttempts = 3,
  baseDelay = 1000
): Promise {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxAttempts - 1) throw error;
      await delay(baseDelay * Math.pow(2, attempt));
    }
  }
}
```

### Deployment Architectures

#### Monolith
- Single deployable unit
- Shared database
- **Pros:** Simpler deployment, easier local development
- **Cons:** Scaling limitations, technology lock-in

#### Microservices
- Independent deployable services
- Separate databases per service
- **Pros:** Independent scaling, technology diversity
- **Cons:** Operational complexity, distributed transactions

#### Serverless (FaaS)
- Function-as-a-Service (AWS Lambda, Cloudflare Workers)
- Event-driven execution
- **Pros:** Zero scaling management, pay-per-use
- **Cons:** Cold starts, vendor lock-in

## Architecture Decision Records (ADR)

### MADR 3.0.0 Template

```markdown
# ADR-[number]: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded by [ADR-number]

## Context
[What is the issue that we're seeing that is motivating this decision or change?]

## Decision
[What is the change that we're proposing and/or doing?]

## Consequences
- **Positive:** [What will be easier or better?]
- **Negative:** [What will be harder or worse?]
- **Risks:** [What might go wrong?]
- **Mitigation:** [How will we mitigate the risks?]
```

## Common Architectural Trade-offs

| Decision | When to Choose | Trade-offs |
|----------|----------------|------------|
| **SQL vs NoSQL** | ACID needed → SQL<br>Schema flexibility → NoSQL | SQL: Schema rigidity<br>NoSQL: Weaker consistency |
| **Monolith vs Microservices** | Small team → Monolith<br>Independent scaling → Microservices | Monolith: Deployment coupling<br>Microservices: Distributed complexity |
| **Sync vs Async** | Immediate response → Sync<br>Background work → Async | Sync: Blocking, timeout risk<br>Async: Complexity, eventual consistency |
| **Stateful vs Stateless** | Simple → Stateless<br>Session required → Stateful | Stateless: Easier scaling<br>Stateful: Sticky sessions needed |

## Reference

This is a reference document extracted from the `super-dev:architecture-agent`. For full agent behavior during Phase 5.3, invoke:

```
Task(subagent_type: "super-dev:architecture-agent", prompt: "Design architecture for: [feature]")
```
