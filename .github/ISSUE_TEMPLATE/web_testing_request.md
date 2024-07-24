---
name: Web Testing Request
about: Web workflow for full site
title: ''
labels: 'QA'
assignees: ''

---

### Background

[FILL ME IN]

### Goals
1. Workflow for FOO user (`foo_user`)
1. Workflow for BAR user (`bar_user`)
1. Test any controls for user testing

### Requirements
1. Work on a feature branch
1. Commits that make progress on this ticket should include the text
   `Ref #[issuenumber]` so that the change is easily traceable once the
   branch is merged and deleted.  (For commits that are purely for PEP8
   style or code structure, do not reference this issue number.)
1. Removal of stale tests is allowed
1. Tests must pass
1. Code review

### Tasks (draft)

Flags:
- `USER_TESTING_FOO_VAR`: Boolean

Valid states:
- ...

#### FOO
Landing:
1. [ ] Impersonate `foo_user`
1. [ ] "Tasks" menu holds "X" item
1. [ ] Clicking link goes to ZZ view

ZZ:
1. [ ] Clicking button yields state label "Done"

`USER_TESTING_FOO_VAR=true`:
- [ ] Special menu exists
    - [ ] X yields Y

`USER_TESTING_FOO_VAR=false`:
- [ ] No special menu exists


#### BAR
