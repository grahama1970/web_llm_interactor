# Task Plan Guide

This document outlines the standard structure and formatting for task planning documents within the project. Following this guide ensures consistency and clarity in task planning across all modules.

## Core Principles

1. **Code Executor vs. Task Creator Gap**: Task plans must assume the code executor may have different knowledge or capabilities than the task creator. Therefore, tasks must be extremely detailed, iterative, and well-defined.

2. **Verification First Development**: Each function or feature must be verified to work correctly before moving to the next task. Every function should include a demonstration mechanism (rich table, JSON output, etc.) that allows both humans and agents to easily confirm correct behavior.

3. **Version Control Discipline**: Start each new task with a git commit to enable rollback if needed. Create git tags at the completion of major tasks or phases.

4. **Testing Strategy**: Create tests after functionality is working correctly, not during active development. Initial focus should be on verifying function output via demonstration.

5. **Human-Friendly Documentation**: Always provide a clear usage table for CLI functions that humans can easily understand and try.

## Task Document Structure

All task documents should follow this standard structure:

```markdown
# Task Title ⏳ Status Indicator

**Objective**: Concise description of the overall task goal.

**Requirements**:
1. High-level requirement 1
2. High-level requirement 2
3. High-level requirement 3
...

## Overview

Brief contextual information about the task, explaining why it's needed and its relationship to the project.

## Implementation Tasks

### Task 1: Descriptive Name ⏳ Status Indicator

**Implementation Steps**:
- [ ] Step 1.1 (Create function skeleton with detailed docstring)
- [ ] Step 1.2 (Implement core functionality with minimal complexity)
- [ ] Step 1.3 (Add verification output - rich table, JSON, etc.)
- [ ] Step 1.4 (Verify function works as expected with example inputs)
- [ ] Step 1.5 (Git commit working function)
...

**Technical Specifications**:
- Technical detail 1
- Technical detail 2
- Technical detail 3
...

**Verification Method**:
- Specific verification output format (rich table, JSON, etc.)
- Example inputs and expected outputs
- How to interpret verification results

**Acceptance Criteria**:
- Criterion 1
- Criterion 2
- Criterion 3
...

### Task 2: Descriptive Name ⏳ Status Indicator

**Implementation Steps**:
- [ ] Step 2.1
- [ ] Step 2.2
- [ ] Step 2.3
...

**Technical Specifications**:
- Technical detail 1
- Technical detail 2
- Technical detail 3
...

**Verification Method**:
- Specific verification output format (rich table, JSON, etc.)
- Example inputs and expected outputs
- How to interpret verification results

**Acceptance Criteria**:
- Criterion 1
- Criterion 2
- Criterion 3
...

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| `function1` | What it does | `command --arg value` | Example output |
| `function2` | What it does | `command --arg value` | Example output |
| ... | ... | ... | ... |

## Version Control Plan

- **Initial Commit**: Create before starting any implementation
- **Function Commits**: After each function is implemented and verified
- **Task Commits**: Upon completion of each major task
- **Phase Tags**: Create git tag after completing each phase
- **Rollback Strategy**: How to recover from implementation errors

## Resources

**Package Research**:
- Package 1 - Research notes
- Package 2 - Research notes
...

**Related Documentation**:
- Link to relevant documentation 1
- Link to relevant documentation 2
...

## Progress Tracking

- Start date: [Date]
- Current phase: [Planning/Implementation/Testing/Review]
- Expected completion: [Date]
- Completion criteria: [Specific criteria]

## Context Management

When context length is running low during implementation, use the following approach to compact and resume work:

1. Issue the `/compact` command to create a concise summary of current progress
2. The summary will include:
   - Which tasks are completed/in-progress/pending
   - Current focus and status
   - Known issues or blockers
   - Next steps to resume work
   
3. **Resuming Work**:
   - Issue `/resume` to show the current status and continue implementation
   - All completed tasks will be marked accordingly 
   - Work will continue from the last in-progress item

**Example Compact Summary Format**:
```
COMPACT SUMMARY:
Completed: Tasks 1.1-1.7 (describe key completed functionality)
In Progress: Task 1.8 (describe current work)
Pending: Tasks 2-5 (list major pending tasks)
Issues: Any current blockers or issues
Next steps: Specific next action items
```

---

This task document serves as a memory reference for implementation progress. Update status emojis and checkboxes as tasks are completed to maintain continuity across work sessions.

## Status Indicators

Use these standard status indicators in your task documentation:

- ⏳ Not Started - Task is defined but work hasn't begun
- ⏳ In Progress - Work on the task has started but isn't complete
- ✅ Completed - Task has been finished and meets acceptance criteria
- ⚠️ Blocked - Progress is blocked by an external dependency
- ❌ Cancelled - Task has been cancelled or is no longer needed

## Implementation Steps Guidelines

- Make steps extremely granular and detailed
- Always follow this pattern for function development:
  1. Create function skeleton with detailed docstring
  2. Implement core functionality with minimal complexity
  3. Add verification output (rich table, JSON, etc.)
  4. Verify function works with example inputs
  5. Git commit the working function
- Use checkboxes for tracking completion: `- [ ]` (incomplete) and `- [x]` (complete)
- Number steps hierarchically (e.g., 1.1, 1.2, etc.) for easy reference
- Include specific file paths and function names

## Verification Methods

Every function must include a clear, concrete verification method that produces evidence of correct functionality:

1. **Rich Table Output**: For tabular data, use rich.Table to display results
2. **JSON Verification**: For complex data structures, output formatted JSON
3. **Example-based Verification**: Include example inputs and expected outputs
4. **Visual Verification**: For UI components or visualizations
5. **Log-based Verification**: For background processes or services

**Critical Verification Requirements**:

1. **No Mocking Core Functionality**: Never mock the core functionality being tested
2. **Concrete Examples**: Use real data and show actual outputs, not hypothetical ones
3. **Comparison Against Expected Results**: Always compare actual outputs against expected results
4. **Detailed Failure Information**: Report exactly what failed and how
5. **Human-Verifiable**: Outputs must be easy for humans to verify independently 
6. **Self-Testing Functions**: Each module should include a main block with a simple validation function
7. **Comprehensive Testing**: Test edge cases, not just happy paths

❌ NEVER claim "all tests pass" unless they've been run and actually pass! ❌

## CLI Function Documentation

Every task plan must include a usage table that clearly documents CLI functions:

```markdown
| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| `function_name` | Brief description | `command --arg value` | What to expect |
```

## Testing Strategy

- Focus on verification during development
- Create formal tests after functionality is working correctly
- Test categories should include:
  - Unit tests for individual functions
  - Integration tests for connected components
  - End-to-end tests for complete workflows

## Best Practices

1. **Extreme Clarity**: Write tasks assuming the executor has minimal context
2. **Step-by-Step Instructions**: Provide precise, unambiguous implementation steps
3. **Iterative Development**: Build and verify one small piece at a time
4. **Continuous Verification**: Always include verification steps for each function
5. **Version Control Discipline**: Commit frequently, especially after verification
6. **Human-Friendly Documentation**: Ensure humans can easily use and verify the implementation

## Task File Location

Task plan documents should be stored in the appropriate location:
- Module-specific tasks: `src/complexity/[module_name]/tasks/`
- Project-level tasks: `task.md` in the project root
- Integration tasks: `src/complexity/[module_name]/tasks/integration_task.md`

## Example Task Document

See `src/complexity/gitgit/tasks/001_advanced_parsing_integration_task.md` for a complete example of a properly formatted task document.