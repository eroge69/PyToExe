import mido
from music21 import converter, note, stream

def midi_to_musicxml(midi_file, output_file):
    midi_data = mido.MidiFile(midi_file)
    score = stream.Score()

    for track in midi_data.tracks:
        part = stream.Part()
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                n = note.Note(msg.note)
                n.quarterLength = msg.time / midi_data.ticks_per_beat
                part.append(n)
        score.append(part)

    score.write('musicxml', output_file)

# Example usage:
midi_to_musicxml("input.mid", "output.musicxml")