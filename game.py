import pygame
import fluidsynth
import threading

# Initialize Pygame
pygame.init()
pygame.mixer.quit()  # Ensure pygame doesn't use its own sound system

# Start FluidSynth
fs = fluidsynth.Synth()
fs.start(driver="coreaudio")  # Use CoreMIDI on Mac
sfid = fs.sfload("/Users/samuelshen/Documents/soundfonts/Electric_guitar.sf2")  # Load the SoundFont
fs.program_select(0, sfid, 0, 0)  # Select bank 0, program 0 (Electric Guitar)

# Define "Mary Had a Little Lamb" melody (MIDI notes)
mary_lamb = [
    64, 62, 60, 62, 64, 64, 64,  # Mary had a little lamb
    62, 62, 62, 64, 67, 67,       # Little lamb, little lamb
    64, 62, 60, 62, 64, 64, 64,  # Mary had a little lamb
    62, 62, 64, 62, 60, 60        # Its fleece was white as snow
]

correct_indices = [
    2, 1, 0, 1, 2, 2, 2,  # Mary had a little lamb
    1, 1, 1, 2, 3, 3,
    2, 1, 0, 1, 2, 2, 2,  # Mary had a little lamb
    1, 1, 2, 1, 0, 0     # Its fleece was white as snow
]

# Allowed keys
ALLOWED_KEYS = {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_SPACE}

# Game Settings
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("MIDI Music Game")
font = pygame.font.Font(None, 36)

KEY_BUFFER = set()  # Store currently held keys
increments = [0, 1, 2, 3]  # Possible incorrect note offsets
current_note_index = 0  # Track which note is playing


def generate_note_set(correct_index):
    """Generate a set of notes including the correct one and three variations."""
    base_note = mary_lamb[current_note_index]
    return [base_note + increment - correct_index for increment in increments]


note_set = generate_note_set(correct_indices[current_note_index])


def draw_screen():
    """Draw the UI with four notes and highlight selections."""
    screen.fill((0, 0, 0))

    # Display next note prompt
    correct_text = font.render(f"Next Note: {correct_indices[current_note_index] + 1}", True, (255, 255, 255))
    screen.blit(correct_text, (100, 20))

    # Display notes
    for i, note in enumerate(note_set):
        color = (255, 255, 255)  # Default white
        if pygame.K_1 + i in KEY_BUFFER:  # Highlight selected keys
            color = (0, 255, 0) if i == correct_indices[current_note_index] else (255, 0, 0)

        text = font.render(f"{i + 1}: {note}", True, color)
        screen.blit(text, (50, 50 + i * 40))

    pygame.display.flip()


def play_note(keys_pressed, note_set_copy):
    """Play notes for the keys pressed."""
    for key in keys_pressed:
        index = key - pygame.K_1
        fs.noteon(0, note_set_copy[index], 100)  # Channel 0, Note, Velocity 100

    pygame.time.delay(500)  # Hold note duration

    for key in keys_pressed:
        index = key - pygame.K_1
        fs.noteoff(0, note_set_copy[index])


running = True
while running:
    draw_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and event.key in ALLOWED_KEYS:
            KEY_BUFFER.add(event.key)

        elif event.type == pygame.KEYUP and event.key in ALLOWED_KEYS:
            KEY_BUFFER.discard(event.key)

    if pygame.K_SPACE in KEY_BUFFER:
        KEY_BUFFER.remove(pygame.K_SPACE)  # Ignore space bar itself

        pressed_keys = list(KEY_BUFFER)  # Convert to list to maintain order
        if pressed_keys:
            # Pass a copy of note_set to avoid modification issues
            threading.Thread(target=play_note, args=(pressed_keys, note_set.copy()), daemon=True).start()

            # Move to the next note
            current_note_index = (current_note_index + 1) % len(mary_lamb)
            note_set = generate_note_set(correct_indices[current_note_index])

pygame.quit()
fs.delete()
