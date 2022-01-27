# Turkish Dictionary for Anki

![Add-on's icon](src/icon.png)

An [Anki](https://apps.ankiweb.net/) add-on to look up Turkish vocabulary and fill notes with information
from the official [TDK dictionary](https://sozluk.gov.tr/).

Currently, the add-on queries word definitions, example sentences, and pronunciations from the dictionary.

The add-on provides an editor button to fill the current note,
and a browser menu item under the Edit menu to fill selected notes in bulk.

It also comes with a template filter named `{{trdict-audio}}` to generate pronunciations
for a field's contents on the fly that can be used by typing something like this in a [card template](https://docs.ankiweb.net/templates/intro.html):
```
{{trdict-audio:Front}}
```
Only works on Anki 2.1.49+ for now.

## TODO
- [ ] Save the most recently used field mappings for each notetype
- [ ] Upload a GitHub release
- [ ] Add interface to look up words
