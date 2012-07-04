Feature: Save and persist configuration
  In order to save program configuration
  As a program user
  I want to be able configure the program and have my changes persist between runs

  Scenario Outline: Required configuration specified on command line
    Given my key is <key>
    And my type is <type>
    And my value is <value>
    When I start the program
    And I require the key
    And I validate the configuration with command-line options
    Then my configuration is available

    Examples:
      | key       | value           | type |
      | verbosity | 10              | int  |
      | lines     | 20              | int  |
      | name      | Program Options | str  |
      | debug     | True            | bool |
      
  Scenario Outline: Required configuration previously saved
    Given my key is <key>
    And my type is <type>
    And my value is <value>
    When I start the program
    And I require the key
    And my key and value have been previously saved
    And I validate the configuration with the previously saved values
    Then my configuration is available
    
    Examples:
      | key       | value           | type |
      | verbosity | 10              | int  |
      | lines     | 20              | int  |
      | name      | Program Options | str  |
      | debug     | True            | bool |
      
  Scenario Outline: Required configuration has default value
    Given my key is <key>
    And my type is <type>
    Given my value is <value>
    When I start the program
    And I require the key with a default value
    And I validate the configuration with the default values
    Then my configuration is available
            
    Examples:
      | key       | value           | type |
      | verbosity | 10              | int  |
      | lines     | 20              | int  |
      | name      | Program Options | str  |
      | debug     | True            | bool |

  Scenario Outline: Required configuration has callback
    Given my key is <key>
    And my type is <type>
    And my value is <value>
    When I start the program
    And I require the key with a callback
    And I validate the configuration with the callback
    Then my configuration is available

    Examples:    
      | key       | value           | type |
      | verbosity | 10              | int  |
      | lines     | 20              | int  |
      | name      | Program Options | str  |
      | debug     | True            | bool |
      
  Scenario Outline: Required configuration with no default or callback
    Given my key is <key>
    And my type is <type>
    When I start the program
    And I require the key
    Then the program fails to validate the configuration

    Examples:
      | key       | type |
      | verbosity | int  |
      | lines     | int  |
      | name      | str  |
      | debug     | bool |
      
  Scenario Outline: Optional configuration
    Given my key is <key>
    And my type is <type>
    When I start the program
    And I specify the key as optional
    Then I validate the configuration without the optional configuration provided

    Examples:
      | key       | type |
      | verbosity | int  |
      | lines     | int  |
      | name      | str  |
      | debug     | bool |
      
  Scenario Outline: Attempt to add duplicate key
    Given my key is <key>
    And my type is <type>
    When I start the program
    And I require the key
    Then I cannot require the key again
        
    Examples:
      | key       | type |
      | verbosity | int  |
      | lines     | int  |
      | name      | str  |
      | debug     | bool |
