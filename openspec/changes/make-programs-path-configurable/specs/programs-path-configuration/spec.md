# Programs Path Configuration Spec

## ADDED Requirements

### Requirement: CLI Option for Data File Path
abm_check CLIは`--data-file`オプションを受け入れ、任意のYAMLファイルをデータベースとして使用できる必要があります。

#### Scenario: User specifies custom data file path
ユーザーがCLIで`--data-file`オプションを使用して任意のファイルパスを指定すると、そのファイルがデータベースとして使用されます。

```gherkin
Given a user with abm_check installed
When the user runs `abm_check add --data-file custom_programs.yaml <program_id>`
Then the program information should be saved to custom_programs.yaml
And commands like `abm_check list` should read from custom_programs.yaml
```

### Requirement: Default Path Preservation
CLIで`--data-file`オプションが指定されない場合、デフォルトの`programs.yaml`が使用される必要があります。

#### Scenario: User does not specify custom data file path
ユーザーがCLIで`--data-file`オプションを指定しない場合、既定の`programs.yaml`ファイルが使用されます。

```gherkin
Given a user with abm_check installed
When the user runs `abm_check add <program_id>`
Then the program information should be saved to programs.yaml
```

### Requirement: Option Precedence
CLIオプションは設定ファイルよりも優先され、設定ファイルよりも優先して使用されます。

#### Scenario: CLI option overrides config file setting
CLIで`--data-file`オプションが指定された場合、設定ファイルで定義された`programs_file`の値よりもCLIオプションが優先されます。

```gherkin
Given a config file with programs_file set to 'config_programs.yaml'
When the user runs `abm_check add --data-file cli_programs.yaml <program_id>`
Then the program information should be saved to cli_programs.yaml, not config_programs.yaml
```

## MODIFIED Requirements

### Requirement: Storage Component Accepts File Path
`ProgramStorage`クラスは、コンストラクタでファイルパスを受け入れ、CLIから渡されたファイルパスを使用できる必要があります。

#### Scenario: ProgramStorage uses custom file path
`ProgramStorage`がファイルパスを受け取ると、指定されたファイルを使用してデータの保存と読み込みを行います。

```gherkin
Given a ProgramStorage instance with a custom file path
When I call save_program() or load_programs()
Then the operations should be performed on the specified file path
```