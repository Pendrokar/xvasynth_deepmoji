# xVASynth DeepMoji Plugin

A plugin for DanRuta/xVASynth

Link to plugin on Nexus Mods page: [https://www.nexusmods.com/skyrimspecialedition/mods/107142?tab=description](https://www.nexusmods.com/skyrimspecialedition/mods/107142?tab=description)

# How it works?

During TTS synthesis, the plugin adjusts the 4 possible emotional modifier values of phonemes equaly for xVAPitch (v3) models.

* Text is given to DeepMoji for analysis and it returns the probabilities of what emojis would humans attach to that text. Also a previous sentence is added for better flow.
* By default, 10 out of the 64 highest probable emojis are taken from the DeepMoji analysis
* emoji_unicode_emotions.csv file contains the 64 emojis and how they may affect the 4 emotional modifiers of xVASynth. 0-100
* The 10 emojis are compared against the CSV and their values summed up
* Emotional modifiers (Angry, Happy, Sad) are exclusive, only the highest scored one gets applied.
* Surprise emotion is always somewhat applied. Unless when the sum of Surprise and Happy values are too high, then only one is applied. "More than happy" 😬
* There is also a ratio amplifier. Which gets increased if there are one or more exclamation marks within the sentence. This ratio is multiplied with the final emotional modifier values.
* At a certain sadness value threshold, the audio length will be increased.

After applied, these values can be seen in the xVASynth editor as well.
