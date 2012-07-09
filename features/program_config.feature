Feature: Save and persist configuration
  In order to save program configuration
  As a program user
  I want to be able configure the program and have my changes persist between runs

  Scenario: Required configuration specified on command line
    Given I have an example configuration
    And I require the configuration with no fallback
    When I validate the configuration with command-line options with persistence
    Then my configuration is available
      
  Scenario: Required configuration previously saved
    Given I have an example configuration
    And I require the configuration with no fallback
    When I validate the configuration with a previously saved configuration
    Then my configuration is available
    
  Scenario: Required configuration has default value
    Given I have an example configuration
    And I require the configuration with default values
    When I validate the configuration without command-line options without persistence
    Then my configuration is available
            
  Scenario: Required configuration has callback
    Given I have the configuration:
      | key       | value | help                     | type | is_persistent | 
      | verbosity | 3     | how much output to print | int  | False         |
    And I require the configuration with a callback
    When I validate the configuration without command-line options with persistence
    Then my configuration is available

  Scenario: Required configuration with no default or callback
    Given I have an example configuration
    And I require the configuration with no fallback
    Then the program fails to validate the configuration
      
  Scenario: Optional configuration
    Given I have an example configuration
    And I specify the configuration as optional
    Then I validate the configuration without command-line options without persistence
      
  Scenario: Attempt to add duplicate configuration
    Given I have an example configuration
    And I require the configuration with no fallback
    Then I cannot require the configuration again
      
#  Scenario: Attempt to set configuration that has not been required
#    Given I have an example configuration
#    Then I cannot set the configuration
    
  Scenario: Default configuration is never persisted
    Given I have the configuration:
      | key       | value | help                     | type | is_persistent | 
      | verbosity | 3     | how much output to print | int  | True          |
    And I require the configuration with default values
    Then I validate the configuration without command-line options without persistence
    
  Scenario: Default configuration on the command line is not persisted
    Given I have the configuration:
      | key       | value | help                     | type | is_persistent | 
      | verbosity | 3     | how much output to print | int  | True          |
    And I require the configuration with default values
    Then I validate the configuration with command-line options without persistence