## Test notes

### Run model

Command examples:

```bash
python bmk.py --batch_size 3 --num_beams 4
python openai_bmk.py --batch_size 3 --num_beams 4 --profile
```

### New Results (20241202)

Obtained from

```bash
bash diff_outputs.sh <path/to/audio>
```

- On audio [audio_teapot.mp3](audios/audio_teapot.mp3):

  <details>
    <summary> Word-level timestamps diff </summary>

  ```diff
   start  end     word
   -----  ---     ----
  -1.06   1.46    Last
  -1.46   1.82    Halloween,
  +0.00   1.46    Last
  +1.46   2.02    Halloween,
   2.02   2.16    M
   2.16   2.42    came
   2.42   2.54    to
   2.54   2.70    work
   2.70   2.86    in
   2.86   2.96    a
   2.96   3.10    tea
   3.10   3.32    cup
  -3.32   3.74    costume.
  +3.32   4.62    costume.
   4.62   4.74    It
   4.74   4.88    says
   4.88   5.08    a
   5.08   5.18    lot
   5.18   5.36    about
   5.36   5.56    a
   5.56   5.74    person
   5.74   5.90    that
   5.90   6.02    she
   6.02   6.26    could
   6.26   6.34    come
   6.34   6.48    to
   6.48   6.62    work
   6.62   6.94    dresses
   6.94   7.20    a
   7.20   7.30    tea
  -7.30   7.60    cup.
  -7.96   8.08    I
  -8.08   8.36    wondered
  +7.30   7.96    cup.
  +7.96   8.10    I
  +8.10   8.36    wondered
   8.36   8.72    whether
   8.72   9.08    Mark
   9.08   9.28    would
   9.28   9.48    come
   9.48   9.60    to
   9.60   9.76    work
   9.76   10.12   dressed
   10.12  10.24   in
   10.24  10.70   a
   10.70  11.06   complimentary
  -11.06  11.76   costume,
  -12.26  12.44   like
  -12.44  12.54   a
  -12.54  12.72   tea
  -12.72  13.02   pot.
  +11.06  11.70   costume
  +11.70  12.44   like
  +12.44  12.56   a
  +12.56  12.72   tea
  +12.72  13.58   pot.
   13.58  13.70   I
   13.70  13.86   spent
   13.86  14.02   the
   14.02  14.30   morning
  -14.30  14.56   in
  -14.56  14.64   a
  -14.64  14.70   set
  -14.70  14.96   of
  +14.30  14.68   instead
  +14.68  14.96   of
   14.96  15.38   frenetic
  -15.38  15.80   dread,
  -15.98  16.14   eager
  -16.14  16.32   to
  +15.38  15.98   dread,
  +15.98  16.16   eager
  +16.16  16.32   to
   16.32  16.48   see
   16.48  16.68   what
   16.68  16.90   Mark
  -16.90  17.16   would
  -17.16  17.24   be
  -17.24  17.56   wearing,
  +16.90  17.14   would
  +17.14  17.24   be
  +17.24  17.78   wearing,
   17.78  17.86   yet
   17.86  18.22   afraid
   18.22  18.50   to
  -18.50  18.82   see.
  +18.50  20.10   see.
  ```
  </details>

- On audio [1272-141231-0002.mp3](audios/1272-141231-0002.mp3):

  Word-level timestamps diff:

  ```diff
   start  end     word
   -----  ---     ----
   0.00   0.72    The
   0.72   0.84    cut
   0.84   1.02    on
   1.02   1.24    his
   1.24   1.54    chest
   1.54   2.10    still
   2.10   2.42    dripping
  -2.42   2.90    blood.
  +2.42   3.74    blood.
   3.74   3.98    The
   3.98   4.16    ache
   4.16   4.36    of
   4.36   4.54    his
   4.54   5.02    overstrain
  -5.02   5.62    dyes.
  +5.02   6.32    dyes.
   6.32   6.50    Even
   6.50   6.76    the
   6.76   7.14    soaring
   7.14   7.58    arena
   7.58   8.06    around
   8.06   8.32    him
   8.32   8.54    with
   8.54   9.08    thousands
   9.08   9.44    of
  -9.44   10.04   spectators,
  +9.44   10.70   spectators,
   10.70  11.52   retrievalidies
   11.52  11.80   not
   11.80  12.12   worth
   12.12  12.46   thinking
  -12.46  12.92   about.
  +12.46  13.30   about.
  ```

### Old Results (before 20241120)

Word-level timestamps

The timestamps of words for ORT look later than the reference, which needs further investigation.

- On audio [audio_teapot.mp3](audios/audio_teapot.mp3):
  - reference ([ref.py](ref.py)):

    <details>
      <summary> Word-level timestamps </summary>

    ```text
    start   end      word
    -----   ---      ----
    1.06    1.46     Last
    1.46    1.82     Halloween,
    2.02    2.16     M
    2.16    2.42     came
    2.42    2.54     to
    2.54    2.70     work
    2.70    2.86     in
    2.86    2.96     a
    2.96    3.10     tea
    3.10    3.32     cup
    3.32    3.74     costume.
    4.62    4.74     It
    4.74    4.88     says
    4.88    5.08     a
    5.08    5.18     lot
    5.18    5.36     about
    5.36    5.56     a
    5.56    5.74     person
    5.74    5.90     that
    5.90    6.02     she
    6.02    6.26     could
    6.26    6.34     come
    6.34    6.48     to
    6.48    6.62     work
    6.62    6.94     dresses
    6.94    7.20     a
    7.20    7.30     tea
    7.30    7.60     cup.
    7.96    8.08     I
    8.08    8.36     wondered
    8.36    8.72     whether
    8.72    9.08     Mark
    9.08    9.28     would
    9.28    9.48     come
    9.48    9.60     to
    9.60    9.76     work
    9.76    10.12    dressed
    10.12   10.24    in
    10.24   10.70    a
    10.70   11.06    complimentary
    11.06   11.76    costume,
    12.26   12.44    like
    12.44   12.54    a
    12.54   12.72    tea
    12.72   13.02    pot.
    13.58   13.70    I
    13.70   13.86    spent
    13.86   14.02    the
    14.02   14.30    morning
    14.30   14.56    in
    14.56   14.64    a
    14.64   14.70    set
    14.70   14.96    of
    14.96   15.38    frenetic
    15.38   15.80    dread,
    15.98   16.14    eager
    16.14   16.32    to
    16.32   16.48    see
    16.48   16.68    what
    16.68   16.90    Mark
    16.90   17.16    would
    17.16   17.24    be
    17.24   17.56    wearing,
    17.78   17.86    yet
    17.86   18.22    afraid
    18.22   18.50    to
    18.50   18.82    see.
    ```
    </details>

  - ORT ([bmk.py](bmk.py)):

    <details>
      <summary> Word-level timestamps </summary>

    ```text
    start       end     word
    -----       ---     ----
    2.22        2.46    Last
    2.46        2.70    Halloween,
    2.70        2.88    M
    2.88        3.02    came
    3.02        3.14    to
    3.14        3.36    work
    3.36        3.76    in
    3.76        4.68    a
    4.68        4.76    tea
    4.76        4.90    cup
    4.90        5.20    costume.
    5.20        5.36    It
    5.36        5.48    says
    5.48        5.72    a
    5.72        5.96    lot
    5.96        6.06    about
    6.06        6.26    a
    6.26        6.38    person
    6.38        6.48    that
    6.48        6.62    she
    6.62        6.94    could
    6.94        7.20    come
    7.20        7.32    to
    7.32        7.72    work
    7.72        8.00    dresses
    8.00        8.12    a
    8.12        8.36    tea
    8.36        9.06    cup.
    9.06        9.26    I
    9.26        9.46    wondered
    9.46        9.60    whether
    9.60        9.76    Mark
    9.76        10.08   would
    10.08       10.26   come
    10.26       10.68   to
    10.68       11.12   work
    11.12       11.66   dressed
    11.66       12.44   in
    12.44       12.56   a
    12.56       12.72   complimentary
    12.72       13.02   costume
    13.02       13.66   like
    13.66       13.74   a
    13.74       13.90   tea
    13.90       14.30   pot.
    14.30       14.68   I
    14.68       14.96   spent
    14.96       15.20   the
    15.20       15.40   morning
    15.40       15.72   instead
    15.72       15.98   of
    15.98       16.34   frenetic
    16.34       16.68   dread,
    16.68       16.90   eager
    16.90       17.08   to
    17.08       17.20   see
    17.20       17.62   what
    17.62       17.78   Mark
    17.78       17.92   would
    17.92       18.24   be
    18.24       18.88   wearing,
    18.88       20.72   yet
    20.72       20.72   afraid
    20.72       20.72   to
    20.72       20.72   see.
    ```
    </details>

- On audio [1272-141231-0002.mp3](audios/1272-141231-0002.mp3):
  - reference:

    <details>
      <summary> Word-level timestamps </summary>

    ```text
    start   end      word
    -----   ---      ----
    0.00    0.72     The
    0.72    0.84     cut
    0.84    1.02     on
    1.02    1.24     his
    1.24    1.54     chest
    1.54    2.10     still
    2.10    2.42     dripping
    2.42    2.90     blood.
    3.74    3.98     The
    3.98    4.16     ache
    4.16    4.36     of
    4.36    4.54     his
    4.54    5.02     overstrain
    5.02    5.62     dyes.
    6.32    6.50     Even
    6.50    6.76     the
    6.76    7.14     soaring
    7.14    7.58     arena
    7.58    8.06     around
    8.06    8.32     him
    8.32    8.54     with
    8.54    9.08     thousands
    9.08    9.44     of
    9.44    10.04    spectators,
    10.70   11.52    retrievalidies
    11.52   11.80    not
    11.80   12.12    worth
    12.12   12.46    thinking
    12.46   12.92    about.
    ```
    </details>

  - ORT:

    <details>
      <summary> Word-level timestamps </summary>

    ```text
    start       end     word
    -----       ---     ----
    1.24        1.54    The
    1.54        2.10    cut
    2.10        2.42    on
    2.42        2.94    his
    2.96        3.78    chest
    3.78        4.00    still
    4.00        4.22    dripping
    4.22        4.54    blood.
    4.54        4.86    The
    4.86        5.08    ache
    5.08        5.36    of
    5.36        5.70    his
    5.70        6.52    overstrain
    6.52        7.24    dyes.
    7.24        7.58    Even
    7.58        8.06    the
    8.06        8.58    soaring
    8.58        9.06    arena
    9.06        9.46    around
    9.46        9.72    him
    9.72        10.06   with
    10.06       10.68   thousands
    10.68       10.88   of
    10.88       11.56   spectators,
    11.56       12.84   retrievalidies
    12.84       13.30   not
    13.30       13.30   worth
    13.30       13.30   thinking
    13.30       13.30   about.
    ```
    </details>
