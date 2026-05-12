# Case Execution Report

## Source Document

- File: `소공_손태호_김지태.docx`
- Authors:
  - 2021112087 손태호
  - 2021112039 김지태

## Executed Use/Test Cases

The document included four main use cases and corresponding test cases:

| Test Case ID | Target | Test Data | Result |
| --- | --- | --- | --- |
| `Login-001` | Valid user login | `testuser / test1234` | Pass |
| `Upload-001` | Photo upload with description and keyword | `sample.jpg`, `내 사진`, `travel` | Pass |
| `Search-001` | Search photos by keyword | `travel` | Pass |
| `Message-001` | Send message to photo owner | `Hello` | Pass |

## Execution Command

```powershell
python -m pytest -p no:cacheprovider --basetemp=.pytest_tmp tests
```

## Result

```text
collected 9 items

tests/test_app.py .....                                                  [ 55%]
tests/test_document_cases.py ....                                        [100%]

9 passed
```

## Notes

- The document-specific cases were added to `tests/test_document_cases.py`.
- The search case was executed after login because this project intentionally restricts photo and search features to logged-in users. This follows the project requirement that non-members can only view the user list.
- No application code changes were required after executing the document cases.
