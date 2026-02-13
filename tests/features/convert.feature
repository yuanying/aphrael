Feature: Ebook format conversion
  As a user of aphrael
  I want to convert ebooks between EPUB, MOBI, and AZW3 formats
  So that I can read them on different devices

  Scenario Outline: Convert EPUB to other formats
    Given an EPUB file "<epub_file>"
    When I convert it to "<output_format>" format
    Then the output file should be created
    And the output file should be a valid "<output_format>" file

    Examples:
      | epub_file | output_format |
      | 01.epub   | mobi          |
      | 01.epub   | azw3          |
      | 02.epub   | mobi          |
      | 02.epub   | azw3          |

  Scenario: Convert AZW3 to EPUB
    Given an AZW3 file "01.azw3"
    When I convert it to "epub" format
    Then the output file should be created
    And the output file should be a valid "epub" file

  Scenario: Convert MOBI to EPUB
    Given a MOBI file from converting "01.epub"
    When I convert the MOBI to "epub" format
    Then the output file should be created
    And the output file should be a valid "epub" file

  Scenario: Show help message
    When I run aphrael with "--help"
    Then it should display usage information

  Scenario: Show version
    When I run aphrael with "--version"
    Then it should display version information
