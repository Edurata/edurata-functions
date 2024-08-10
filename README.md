# Edurata functions

This is a collection of data processing functions that can be used on the Edurata platform. The functions are written in Python and Nodejs and are for public use.

## Structure

- `clients`: Contains generic functions that can be used with a whole third party api. For example instead of only a function to write to a google doc file, we have a client function to interact with the whole google docs api. This means that the interface is usually more complex.
- `general`: Contains functions that are not specific to any third party api. For example a function "axios" which is a general http client.
- `internals`: Contains functions that are used internally by the edurata platform but are open source for transparency. For example for the build functions workflow.
- `etl`: Divided into `extract`, `transform` and `load`. Contains functions that are used to extract data from a source, transform it and load it to a destination. For example a function to extract data from a google doc file, transform it to a json and load it to a google sheet. They are more specific than the `clients` functions.