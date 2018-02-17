
Refactor notes.

2018 we need to support multiple grip pipelines. Refactoring code to do this.

Probable design

BaseSensorPipeline class. Class that holds methods common to pipeline tasks
YelloboxSensor class. Class that is responsible for running the yellowbox detection over images.
AutolineSensor class. Class that is responsible for running the autoline (black) floor line detection over
                      images.
DreadbotVisionEngine class. Class that manages capture.
