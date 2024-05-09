# Meetings notes

## Meeting 1.
* **DATE: 2024-02-07**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
*In the meeting we went through the Deadline 1 description about our API and concepts/design in person. All team members were present at the meeting. The API overview was fine, but main concepts' diagram was wrong type. API uses needed more explanation related to the second client: dashboard. Auxiliary service needed more context as we had forgotten to mention our use of SMS in the project. Related work needed more clarification regarding Smart Campus and needed another example of related works.*

### Action points
*We discussed about the "MökkiWahti" and the following key action points were raised during the meeting*
- "Keep it simple", had too many features/functionalities.
- Provided diagram was about the system architecture, not data/concept relations.
- Explain about the second client: dashboard (visualizing data required)
  - Auxiliary service needed explaining (e.g. SMS thing) 
- Related work: Smart Campus
  - Smart Campus didn't use DELETE or PUT, while "not uniform Interface" uses POST and DELETE.
  - Would need to explain more about the Smart Campus.
  - Explaining about the client was lacking.


## Meeting 2.
* **DATE: 2024-02-19**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
*In the meeting we went through the deadline 2 description about our API and database design + implementation. All team members were present at the meeting and the meeting was arranged remotely. We also briefly checked the deadline 1 deliverable but didn't discuss much about it. The database design and diagram was done correctly, though there were some discussions related to the "location" field in "Measurements" and "Sensor" tables. In the database models, models matched the design, but the relationships were slightly lacking related to relation between Sensor and Measurement. In the readme, requirements.txt was enough, but the readme lacked any instructions related to the installation.*

### Action points
*Here are few action points from the meeting:*
- potential location_id mismatch with Measurement and Sensor
- Iván pointed out "location" information being redundant if the sensors never move, but we had implemented them just in case if the sensors were moved for any reason (to make sure it is more robust and accurate).
  - potentially might encounter errors due its redundancy?
  - Sensors/Measurements being "more part of the SQLalchemy side?"
- Database design: some values not marked as "not nullable".
  - "what happens in cases where these values would be null?" / May need to introduce "default values" to prevent error cases where some values change into "null", which should never turn into "null" value.
- In the database model, more information/explanations related to "sensorConfiguration" would be preferred as atm it is not very well explained.
- "Requirements" were correct, but the README.md lacked instructions related to installing the dependencies via pip. Requires thorough documentation.
  - "instructions how to populate DB, how to test them, etc..."



## Meeting 3.
* **DATE: 2024-03-25**
* **ASSISTANTS: Mika Oja**

### Minutes
*We went through the implementation and tests and some parts of the Wiki report. We also discussed about the future deadlines shortly*

### Action points
*Here are few action points from the meeting:*
- Wiki report lacked descriptions on some of the parts.
- In basic implementation pylist tests needed some cleaning
- In Basic Implementation documentation, endpoint documentation needed more information related to return codes and etc.
- Test coverage wasn't high enough and needed more tests/higher score.
- Schema validation lacked description.



## Meeting 4.
* **DATE: [empty]**
* **ASSISTANTS: [empty]**

### Minutes
*There was no meeting 4.*

### Action points
*[empty]*

## Midterm meeting
* **DATE: [empty]**
* **ASSISTANTS: [empty]**

### Minutes
*There was no Midterm meeting.*

### Action points
*[empty]*

## Final meeting
* **DATE: 2024-05-15**
* **ASSISTANTS: Iván Sánchez Milara**

### Minutes
*Summary of what was discussed during the meeting*

-TBA, meeting hasn't yet occurred-

### Action points
*List here the actions points discussed with assistants*




