# alexa-metrolink-skill
An Alexa skill for asking for Metrolink times

Getting Started
---------------

If you just want to use the skill, then it's currently pending approval
by Amazon, but I shall update this shortly.

This works by scraping beta.tfgm.com in lieu of a proper API. It's
definitely not affiliated with TfGM, Metrolink, or anyone like that.

Developing This
---------------

You'll need Python 3.6 installed, and a way of running shell scripts.

    ./bootstrap.sh

This will set up a Virtualenv containing all of the necessary dependencies.
You will now need to run `utilities/update-stop-names.py` to generate
the stop names from the published TfGM data.

There aren't really any tests, but you can run `./test.py` to run a test
interaction. There's also a skipped test in there which will test that
that all the stop names are accessible on the TfGM site.

If you want to run your own version on a real device, go to the
[Alexa developer portal](https://developer.amazon.com/edw/home.html)
and create a new skill. The Interaction Model tab can be populated
with information from the [interaction-model/](interaction-model/) folder.
Put [intent-schema.json](interaction-model/intent-schema.json) into the
intent schema box, then create a Custom Slot Type called `TRAM_STOP_NAME`,
and put [stop-names.txt](interaction-model/stop-names.txt) into that field.
Finally, the [sample-utterances.txt](interaction-model/sample-utterances.txt)
should go into the Sample Utterances box.

If you know a way to automate this, please let me know!

If you want to deploy this, then this is all ready for continuous delivery!
You'll need to have some AWS credentials locally
(`virtualenv/bin/aws configure`) which allow you to create CloudFormation
stacks etc, and you'll need to complete [secrets.json](secrets.json)
with your skill ID from the Alexa dev console, then you can run
`./deploy.sh` which will set up all your infrastructure etc as needed.
This is all defined as a template in
[infrastruction/cloudformation.py](infrastructure/cloudformation.py).

Happy tram travelling!
