# CLI Executability from Any Directory Spec

## MODIFIED Requirements

### Requirement: Installation Enables Global CLI Access
CLIは、インストール後に任意のディレクトリから実行可能でなければならない。

#### Scenario: User installs and runs CLI from any directory
ユーザーがプロジェクトをインストールした後、任意のディレクトリから`abm_check`コマンドを実行できる。

```gherkin
Given a user has installed abm_check via pip
When the user runs `abm_check version` from any directory
Then the command should execute successfully and return version information
```

### Requirement: Clear Installation Instructions
READMEは、CLIをグローバルに実行可能にするための明確な手順を提供しなければならない。

#### Scenario: User follows installation instructions
ユーザーがREADMEの指示に従ってインストールすると、任意のディレクトリからCLIが実行できるようになる。

```gherkin
Given a user follows the installation instructions in README.md
When the user opens a new terminal/command prompt
Then the user should be able to run `abm_check` from any directory
```

## ADDED Requirements

### Requirement: Installation Verification Process
ユーザーは、CLIがグローバルに実行可能であることを確認するための検証手順を実行できる。

#### Scenario: User verifies CLI installation
ユーザーがインストール後に検証手順を実行すると、CLIが正しくインストールされていることを確認できる。

```gherkin
Given a user has installed abm_check
When the user runs the verification command in a new directory
Then the user should receive confirmation that CLI is available globally
```