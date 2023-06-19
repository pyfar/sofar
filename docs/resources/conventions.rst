.. _conventions_introduction:

Introduction
============

SOFA conventions specify what data and metadata must be stored in a SOFA file. Different conventions can be used to store different types of data,e.g., head-related impulse responses or musical instrument directivities.It is advised to always use the conventions that is most specific for thedata.

In the following, SOFA conventions are described in tables with the information

* **Name:** The Name of the data. The prefix *GLOBAL* denotes global attribute, i.e., attributes that pertain the entire data set. Underscores denote attributes that are data specific. E.g., *SourcePosition_Units* denotes the *Units* of the data *SourcePosition*.
* **Type:** The Type of the data.

  * **Attribute:** A verbose description given by a string
  * **Double:** A numeric array of data
  * **String:** A string array of data

* **Default:** The default value
* **Dimensions:** The dimensions of the data. Lower case letters denote the data that sets the dimension.

  * **E:** Number of emitters
  * **R:** Number of receivers
  * **M:** Number of measurements
  * **N:** Number of samples or frequency bins of the data
  * **C:** Number of coordinates (always 3)
  * **I:** Unity dimentions (always 1)
  * **S:** Lengths of the longest string contained in the data (detected automatically)

* **Flags:**

  * **r:** read only data. Data can be written if flag is missing.
  * **m:** mandatory data. Data is optional if flag is missing

.. _conventions:

Conventions
===========

* :ref:`FreeFieldDirectivityTF v1.0 <FreeFieldDirectivityTF_1.0>`
* :ref:`FreeFieldDirectivityTF v1.1 <FreeFieldDirectivityTF_1.1>`
* :ref:`FreeFieldHRIR v1.0 <FreeFieldHRIR_1.0>`
* :ref:`FreeFieldHRTF v1.0 <FreeFieldHRTF_1.0>`
* :ref:`GeneralFIR-E v2.0 <GeneralFIR-E_2.0>`
* :ref:`GeneralFIR v1.0 <GeneralFIR_1.0>`
* :ref:`GeneralSOS v1.0 <GeneralSOS_1.0>`
* :ref:`GeneralTF-E v1.0 <GeneralTF-E_1.0>`
* :ref:`GeneralTF v1.0 <GeneralTF_1.0>`
* :ref:`GeneralTF v2.0 <GeneralTF_2.0>`
* :ref:`SimpleFreeFieldHRIR v1.0 <SimpleFreeFieldHRIR_1.0>`
* :ref:`SimpleFreeFieldHRSOS v1.0 <SimpleFreeFieldHRSOS_1.0>`
* :ref:`SimpleFreeFieldHRTF v1.0 <SimpleFreeFieldHRTF_1.0>`
* :ref:`SimpleFreeFieldSOS v1.0 <SimpleFreeFieldSOS_1.0>`
* :ref:`SimpleHeadphoneIR v1.0 <SimpleHeadphoneIR_1.0>`
* :ref:`SingleRoomMIMOSRIR v1.0 <SingleRoomMIMOSRIR_1.0>`
* :ref:`SingleRoomSRIR v1.0 <SingleRoomSRIR_1.0>`
* :ref:`GeneralFIRE v1.0 (deprecated) <GeneralFIRE_1.0>`
* :ref:`MultiSpeakerBRIR v0.3 (deprecated) <MultiSpeakerBRIR_0.3>`
* :ref:`SimpleFreeFieldHRIR v0.4 (deprecated) <SimpleFreeFieldHRIR_0.4>`
* :ref:`SimpleFreeFieldTF v0.4 (deprecated) <SimpleFreeFieldTF_0.4>`
* :ref:`SimpleFreeFieldTF v1.0 (deprecated) <SimpleFreeFieldTF_1.0>`
* :ref:`SimpleHeadphoneIR v0.1 (deprecated) <SimpleHeadphoneIR_0.1>`
* :ref:`SimpleHeadphoneIR v0.2 (deprecated) <SimpleHeadphoneIR_0.2>`
* :ref:`SingleRoomDRIR v0.2 (deprecated) <SingleRoomDRIR_0.2>`
* :ref:`SingleRoomDRIR v0.3 (deprecated) <SingleRoomDRIR_0.3>`

Current
=======

.. _FreeFieldDirectivityTF_1.0:

**FreeFieldDirectivityTF v1.0**

This conventions stores directivities of acoustic sources (instruments, loudspeakers, singers, talkers, etc) in the frequency domain for multiple musical notes in free field.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - FreeFieldDirectivityTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - We store frequency-dependent data here
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary, but the spatial setup assumes free field.
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Name of the database. Used for classification of the data
   * - GLOBAL_Musician (*attribute*)
     - 
     - 
     - 
     - Narrative description of the musician such as position, behavior, or personal data if not data-protected, e.g., 'Christiane Schmidt sitting on the chair', or 'artificial excitation by R2D2'.
   * - GLOBAL_Description (*attribute*)
     - 
     - 
     - 
     - Narrative description of a measurement. For musical instruments/singers, the note (C1, D1, etc) or the dynamic (pp., ff., etc), or the string played, the playing style (pizzicato, legato, etc.), or the type of excitation (e.g., hit location of a cymbal). For loudspeakers, the system and driver units.
   * - GLOBAL_SourceType (*attribute*)
     - 
     - 
     - m
     - Narrative description of the acoustic source, e.g., 'Violin', 'Female singer', or '2-way loudspeaker'
   * - GLOBAL_SourceManufacturer (*attribute*)
     - 
     - 
     - m
     - Narrative description of the manufacturer of the source, e.g., 'Stradivari, Lady Blunt, 1721' or 'LoudspeakerCompany'
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Position of the microphone array during the measurements.
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - Orientation of the microphone array
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Up vector of the microphone array
   * - ReceiverPosition (*double*)
     - [0, 0, 1]
     - IC, RC, RCM
     - m
     - Positions of the microphones during the measurements (relative to the Listener)
   * - ReceiverPosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Position of the acoustic source (instrument)
   * - SourcePosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition_Reference (*attribute*)
     - 
     - 
     - m
     - Narrative description of the spatial reference of the source position, e.g., for the trumpet, 'The bell'. Mandatory in order to provide a reference across different instruments
   * - SourceView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - Orientation of the acoustic source (instrument)
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceView_Reference (*attribute*)
     - 
     - 
     - m
     - Narrative description of the spatial reference of the source view, e.g., for the trumpet, 'Viewing direction of the bell'. Mandatory in order to provide a reference across different instruments
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Up vector of the acoustic source (instrument)
   * - SourceUp_Reference (*attribute*)
     - 
     - 
     - m
     - Narrative description of the spatial reference of the source up, e.g., for the trumpet, 'Along the keys, keys up'. Mandatory in order to provide a reference across different instruments
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - A more detailed structure of the Source. In a simple settings, a single Emitter is considered that is collocated with the source.
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - EmitterDescription (*string*)
     - ['']
     - IS, MS
     - 
     - A more detailed structure of the source. In a simple setting, a single Emitter is considered that is collocated with the source. In a more complicated setting, this may be the strings of a violin or the units of a loudspeaker.
   * - MIDINote (*double*)
     - 0
     - I, M
     - 
     - Defines the note played by the source during the measurement. The note is specified a MIDI note by the [https://www.midi.org/specifications-old/item/the-midi-1-0-specification MIDI specifications, version 1.0]. Not mandatory, but recommended for tonal instruments.
   * - Description (*string*)
     - ['']
     - MS
     - 
     - This variable is used when the description varies with M.
   * - SourceTuningFrequency (*double*)
     - 440
     - I, M
     - 
     - Frequency (in hertz) to which a musical instrument is tuned to corresponding to the note A4 (MIDINote=69). Recommended for tonal instruments.
   * - N (*double*)
     - 0
     - N
     - m
     - Frequency values
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - 
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - Units used for N
   * - Data_Real (*double*)
     - 0
     - mrn
     - m
     - Real part of the complex spectrum. The default value 0 indicates that all data fields are initialized with zero values.
   * - Data_Imag (*double*)
     - 0
     - MRN
     - m
     - Imaginary part of the complex spectrum

:ref:`back to top <conventions>`

.. _FreeFieldDirectivityTF_1.1:

**FreeFieldDirectivityTF v1.1**

This conventions stores directivities of acoustic sources (instruments, loudspeakers, singers, talkers, etc) in the frequency domain for multiple musical notes in free field.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - FreeFieldDirectivityTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.1
     - 
     - r, m
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - We store frequency-dependent data here
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary, but the spatial setup assumes free field.
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Name of the database. Used for classification of the data
   * - GLOBAL_Musician (*attribute*)
     - 
     - 
     - 
     - Narrative description of the musician such as position, behavior, or personal data if not data-protected, e.g., 'Christiane Schmidt sitting on the chair', or 'artificial excitation by R2D2'.
   * - GLOBAL_Description (*attribute*)
     - 
     - 
     - 
     - Narrative description of a measurement. For musical instruments/singers, the note (C1, D1, etc) or the dynamic (pp., ff., etc), or the string played, the playing style (pizzicato, legato, etc.), or the type of excitation (e.g., hit location of a cymbal). For loudspeakers, the system and driver units.
   * - GLOBAL_SourceType (*attribute*)
     - 
     - 
     - m
     - Narrative description of the acoustic source, e.g., 'Violin', 'Female singer', or '2-way loudspeaker'
   * - GLOBAL_SourceManufacturer (*attribute*)
     - 
     - 
     - m
     - Narrative description of the manufacturer of the source, e.g., 'Stradivari, Lady Blunt, 1721' or 'LoudspeakerCompany'
   * - GLOBAL_EmitterDescription (*attribute*)
     - 
     - 
     - 
     - A more detailed structure of the source. In a simple setting, a single Emitter is considered that is collocated with the source. In a more complicated setting, this may be the strings of a violin or the units of a loudspeaker.
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Position of the microphone array during the measurements.
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - Orientation of the microphone array
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Up vector of the microphone array
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RC, RCM
     - m
     - Positions of the microphones during the measurements (relative to the Listener)
   * - ReceiverPosition_Type (*attribute*)
     - spherical
     - 
     - m
     - Type of the coordinate system used.
   * - ReceiverPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - Units of the coordinates.
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Position of the acoustic source (instrument)
   * - SourcePosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition_Reference (*attribute*)
     - 
     - 
     - m
     - Narrative description of the spatial reference of the source position, e.g., 'The bell' for a trumpet or 'On the front plate between the low- and mid/high-frequency unit' for a loudspeaker. Mandatory in order to provide a reference across different sources.
   * - SourceView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - View vector for the orientation.
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceView_Reference (*attribute*)
     - 
     - 
     - m
     - Narrative description of the spatial reference of the source view, e.g., 'Viewing direction of the bell' for a trumpet or 'Perpendicular to the front plate' for a loudspeaker. Mandatory in order to provide a reference across different sources.
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Up vector of the acoustic source (instrument)
   * - SourceUp_Reference (*attribute*)
     - 
     - 
     - m
     - Narrative description of the spatial reference of the source up, e.g., 'Along the keys, keys up' for a trumpet or 'Perpendicular to the top plate' for a loudspeaker. Mandatory in order to provide a reference across different sources.
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eC, eCM
     - m
     - Position. In a simple settings, a single emitter is considered that is collocated with the source.
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - EmitterDescriptions (*string*)
     - ['']
     - MS, ES, MES
     - 
     - A more detailed description of the Emitters. For example, this may be the strings of a violin or the units of a loudspeaker.
   * - MIDINote (*double*)
     - 0
     - I, M
     - 
     - Defines the note played by the source during the measurement. The note is specified a MIDI note by the [https://www.midi.org/specifications-old/item/the-midi-1-0-specification MIDI specifications, version 1.0]. Not mandatory, but recommended for tonal instruments.
   * - Description (*string*)
     - ['']
     - MS
     - 
     - This variable is used when the description varies with M.
   * - SourceTuningFrequency (*double*)
     - 440
     - I, M
     - 
     - Frequency (in hertz) to which a musical instrument is tuned to corresponding to the note A4 (MIDINote=69). Recommended for tonal instruments.
   * - N (*double*)
     - 0
     - N
     - m
     - Frequency values
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - narrative name of N
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - Units used for N
   * - Data_Real (*double*)
     - 0
     - mrn
     - m
     - Real part of the complex spectrum. The default value 0 indicates that all data fields are initialized with zero values.
   * - Data_Imag (*double*)
     - 0
     - MRN
     - m
     - Imaginary part of the complex spectrum

:ref:`back to top <conventions>`

.. _FreeFieldHRIR_1.0:

**FreeFieldHRIR v1.0**

An extension of SimpleFreeFieldHRIR in order to consider more complex data sets described in spatially continuous representation. Each HRTF direction corresponds to an emitter, and a consistent measurement for a single listener and all directions is described by a set of the emitter positions surrounding the listener.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - FreeFieldHRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR-E
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - Short name of the listener (as for example the subject ID).
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Name of the database to which these data belong
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - RCI, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Source position is assumed to be the ListenerPosition in order to reflect Emitters surrounding the Listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - IC, ECI, ECM
     - m
     - Radius in 'spherical harmonics', Position in 'cartesian' and 'spherical'
   * - EmitterPosition_Type (*attribute*)
     - spherical harmonics
     - 
     - m
     - Can be 'spherical harmonics', 'cartesian', or 'spherical'
   * - EmitterPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_IR (*double*)
     - [0, 0]
     - mrne
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IRI, MRI, MRE
     - m
     - Additional delay of each IR (in samples)

:ref:`back to top <conventions>`

.. _FreeFieldHRTF_1.0:

**FreeFieldHRTF v1.0**

This conventions is for HRTFs created under conditions where room information is irrelevant and stored as SH coefficients

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - FreeFieldHRTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF-E
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Name of the database to which these data belong
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - RCI, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Source position is assumed to be the ListenerPosition in order to reflect Emitters surrounding the Listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - IC, ECI, ECM
     - m
     - Radius in 'spherical harmonics', Position in 'cartesian' and 'spherical'
   * - EmitterPosition_Type (*attribute*)
     - spherical harmonics
     - 
     - m
     - Can be 'spherical harmonics', 'cartesian', or 'spherical'
   * - EmitterPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - 
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - narrative name of N
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Real (*double*)
     - [0, 0]
     - mrne
     - m
     - 
   * - Data_Imag (*double*)
     - [0, 0]
     - MRNE
     - m
     - 

:ref:`back to top <conventions>`

.. _GeneralFIR-E_2.0:

**GeneralFIR-E v2.0**

This conventions stores IRs for general purposes, i.e., only the mandatory, SOFA general metadata are pre-defined

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralFIR-E
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 2.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR-E
     - 
     - r, m
     - We use FIR datatype which in addition depends on Emitters (E)
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RC, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - IC, EC, ECM
     - m
     - Each speaker is represented as an emitter. Use EmitterPosition to represent the position of a particular speaker. Size of EmitterPosition determines E
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_IR (*double*)
     - 0
     - mrne
     - m
     - Impulse responses
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - Sampling rate of the samples in Data.IR and Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the sampling rate
   * - Data_Delay (*double*)
     - 0
     - IRE, MRE
     - m
     - Additional delay of each IR (in samples)

:ref:`back to top <conventions>`

.. _GeneralFIR_1.0:

**GeneralFIR v1.0**

This conventions stores IRs for general purposes, i.e., only the mandatory, SOFA general metadata are pre-defined

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralFIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - We store IRs here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RC, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - In order to store different directions/positions around the listener, SourcePosition is assumed to vary
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - 
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - Data_IR (*double*)
     - 0
     - mrn
     - m
     - Impulse responses
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - Sampling rate of the samples in Data.IR and Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the sampling rate
   * - Data_Delay (*double*)
     - 0
     - IR, MR
     - m
     - Additional delay of each IR (in samples)

:ref:`back to top <conventions>`

.. _GeneralSOS_1.0:

**GeneralSOS v1.0**

This conventions follows GeneralFIR but the data is stored as second-order section (SOS) coefficients.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralSOS
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - SOS
     - 
     - r, m
     - Filters described as second-order section (SOS) coefficients
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - 
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RC, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - In order to store different directions/positions around the listener, SourcePosition is assumed to vary
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_SOS (*double*)
     - [[[0, 0, 0, 1, 0, 0]]]
     - mrn
     - m
     - Filter coefficients as SOS coefficients.
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - Sampling rate of the coefficients in Data.SOS and the delay in Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the sampling rate
   * - Data_Delay (*double*)
     - 0
     - IR, MR
     - m
     - Broadband delay (in samples resulting from SamplingRate)

:ref:`back to top <conventions>`

.. _GeneralTF-E_1.0:

**GeneralTF-E v1.0**

This conventions stores TFs depending in the Emiiter for general purposes, i.e., only the mandatory, SOFA general metadata are pre-defined. This convention is based on GeneralTF

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralTF-E
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF-E
     - 
     - r, m
     - We store frequency-dependent data depending on the emitter here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RC, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - In order to store different directions/positions around the listener, SourcePosition is assumed to vary
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - IC, EC, ECM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - Frequency values
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - narrative name of N
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the values given in N
   * - Data_Real (*double*)
     - 0
     - mrne
     - m
     - The real part of the complex spectrum
   * - Data_Imag (*double*)
     - 0
     - MRNE
     - m
     - The imaginary part of the complex spectrum

:ref:`back to top <conventions>`

.. _GeneralTF_1.0:

**GeneralTF v1.0**

This conventions stores TFs for general purposes, i.e., only the mandatory, SOFA general metadata are pre-defined. This convention is based on GeneralFIR.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - We store frequency-dependent data here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - In order to store different directions/positions around the listener, SourcePosition is assumed to vary
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - Frequency values
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - narrative name of N
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the values given in N
   * - Data_Real (*double*)
     - 0
     - mRn
     - m
     - The real part of the complex spectrum
   * - Data_Imag (*double*)
     - 0
     - MRN
     - m
     - The imaginary part of the complex spectrum

:ref:`back to top <conventions>`

.. _GeneralTF_2.0:

**GeneralTF v2.0**

This conventions stores TFs for general purposes, i.e., only the mandatory, SOFA general metadata are pre-defined. This convention is based on GeneralFIR.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 2.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - We store frequency-dependent data here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RC, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - In order to store different directions/positions around the listener, SourcePosition is assumed to vary
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eC, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - Frequency values
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - narrative name of N
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the values given in N
   * - Data_Real (*double*)
     - 0
     - mrn
     - m
     - The real part of the complex spectrum
   * - Data_Imag (*double*)
     - 0
     - MRN
     - m
     - The imaginary part of the complex spectrum

:ref:`back to top <conventions>`

.. _SimpleFreeFieldHRIR_1.0:

**SimpleFreeFieldHRIR v1.0**

This convention set is for HRIRs recorded under free-field conditions or other IRs created under conditions where room information is irrelevant

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldHRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - 
     - 
   * - SourceView (*double*)
     - [1, 0, 0]
     - IC, MC
     - 
     - 
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - Data_IR (*double*)
     - [0, 0]
     - mRn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleFreeFieldHRSOS_1.0:

**SimpleFreeFieldHRSOS v1.0**

This convention set follows SimpleFreeFieldHRIR but the data is stored as second-order section (SOS) coefficients.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldHRSOS
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - SOS
     - 
     - r, m
     - Filters described as second-order section (SOS) coefficients
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_SOS (*double*)
     - [[[0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0]]]
     - mRn
     - m
     - Filter coefficients as SOS coefficients.
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - Sampling rate of the coefficients in Data.SOS and the delay in Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - Broadband delay (in samples resulting from SamplingRate)

:ref:`back to top <conventions>`

.. _SimpleFreeFieldHRTF_1.0:

**SimpleFreeFieldHRTF v1.0**

This conventions is for HRTFs created under conditions where room information is irrelevant

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldHRTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - 
   * - N_LongName (*attribute*)
     - frequency
     - 
     - m
     - narrative name of N
   * - N_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Real (*double*)
     - [0, 0]
     - mRn
     - m
     - 
   * - Data_Imag (*double*)
     - [0, 0]
     - MRN
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleFreeFieldSOS_1.0:

**SimpleFreeFieldSOS v1.0**

This convention set follows SimpleFreeFieldHRIR but the data is stored as second-order section (SOS) coefficients.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldSOS
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - SOS
     - 
     - r, m
     - Filters described as second-order section (SOS) coefficients
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_SOS (*double*)
     - [[[0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0]]]
     - mRn
     - m
     - Filter coefficients as SOS coefficients.
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - Sampling rate of the coefficients in Data.SOS and the delay in Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - Broadband delay (in samples resulting from SamplingRate)

:ref:`back to top <conventions>`

.. _SimpleHeadphoneIR_1.0:

**SimpleHeadphoneIR v1.0**

Conventions for IRs with a 1-to-1 correspondence between emitter and receiver. The main application for this convention is to store headphone IRs recorded for each emitter and each ear.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleHeadphoneIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - We will store IRs here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - Room type is not relevant here
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Correspondence to a database
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - Correspondence to a subject from the database
   * - GLOBAL_ListenerDescription (*attribute*)
     - 
     - 
     - 
     - Narrative description of the listener (or mannequin)
   * - GLOBAL_SourceDescription (*attribute*)
     - 
     - 
     - 
     - Narrative description of the headphones
   * - GLOBAL_SourceManufacturer (*attribute*)
     - 
     - 
     - 
     - Name of the headphones manufacturer
   * - GLOBAL_SourceModel (*attribute*)
     - 
     - 
     - 
     - Name of the headphone model. Must uniquely describe the headphones of the manufacturer
   * - GLOBAL_SourceURI (*attribute*)
     - 
     - 
     - 
     - URI of the headphone specifications
   * - GLOBAL_ReceiverDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the microphones
   * - GLOBAL_EmitterDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the headphone drivers
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Default: Headphones are located at the position of the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - eCI, eCM
     - m
     - Default: Reflects the correspondence of each emitter to each receiver
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceManufacturer (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute SourceManufucturer
   * - SourceModel (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute SourceModel
   * - ReceiverDescriptions (*string*)
     - ['']
     - MS
     - 
     - R-dependent version of the attribute ReceiverDescription
   * - EmitterDescriptions (*string*)
     - ['']
     - MS
     - 
     - E-dependent version of the attribute EmitterDescription
   * - MeasurementDate (*double*)
     - 0
     - M
     - 
     - Optional M-dependent date and time of the measurement
   * - Data_IR (*double*)
     - [0, 0]
     - mRn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

.. _SingleRoomMIMOSRIR_1.0:

**SingleRoomMIMOSRIR v1.0**

Single-room multiple-input multiple-output spatial room impulse responses, depending on Emitters

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SingleRoomMIMOSRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR-E
     - 
     - r, m
     - Shall be FIR-E
   * - GLOBAL_RoomType (*attribute*)
     - shoebox
     - 
     - m
     - Shall be 'shoebox' or 'dae'
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Name of the database. Used for classification of the data.
   * - GLOBAL_RoomShortName (*attribute*)
     - 
     - 
     - 
     - Short name of the Room
   * - GLOBAL_RoomDescription (*attribute*)
     - 
     - 
     - 
     - Informal verbal description of the room
   * - GLOBAL_RoomLocation (*attribute*)
     - 
     - 
     - 
     - Location of the room
   * - GLOBAL_RoomGeometry (*attribute*)
     - 
     - 
     - 
     - URI to a file describing the room geometry.
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ListenerDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ReceiverShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ReceiverDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_SourceShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_SourceDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_EmitterShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_EmitterDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - RoomTemperature (*double*)
     - 0
     - I, M
     - 
     - Temperature during measurements, given in Kelvin.
   * - RoomTemperature_Units (*attribute*)
     - kelvin
     - 
     - 
     - Units of the room temperature
   * - RoomVolume (*double*)
     - 0
     - I, MI
     - 
     - Volume of the room
   * - RoomVolume_Units (*attribute*)
     - cubic metre
     - 
     - 
     - Units of the room volume
   * - RoomCornerA (*double*)
     - [0, 0, 0]
     - IC, MC
     - 
     - 
   * - RoomCornerB (*double*)
     - [1, 2, 3]
     - IC, MC
     - 
     - 
   * - RoomCorners (*double*)
     - 0
     - II
     - 
     - The value of this attribute is to be ignored. It only exist to for RoomCorners:Type and RoomCorners:Units
   * - RoomCorners_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - RoomCorners_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverDescriptions (*string*)
     - ['']
     - RS, RSM
     - 
     - R-dependent version of the attribute ReceiverDescription
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RCI, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - spherical
     - 
     - m
     - Can be of any type enabling both spatially discrete and spatially continuous representations.
   * - ReceiverPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - ReceiverView (*double*)
     - [1, 0, 0]
     - RCI, RCM
     - 
     - 
   * - ReceiverUp (*double*)
     - [0, 0, 1]
     - RCI, RCM
     - 
     - 
   * - ReceiverView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - ReceiverView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - EmitterDescriptions (*string*)
     - ['']
     - ES, ESM
     - 
     - E-dependent version of the attribute EmitterDescription
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - IC, ECI, ECM
     - m
     - Can be of any type enabling both spatially discrete and spatially continuous representations.
   * - EmitterPosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterView (*double*)
     - [1, 0, 0]
     - ECI, ECM
     - 
     - 
   * - EmitterUp (*double*)
     - [0, 0, 1]
     - ECI, ECM
     - 
     - 
   * - EmitterView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - EmitterView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - MeasurementDate (*double*)
     - 0
     - M
     - 
     - Optional M-dependent date and time of the measurement.
   * - Data_IR (*double*)
     - 0
     - mrne
     - m
     - Impulse responses
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - Sampling rate of the samples in Data.IR and Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the sampling rate
   * - Data_Delay (*double*)
     - 0
     - IRI, MRI, MRE
     - m
     - Additional delay of each IR (in samples)

:ref:`back to top <conventions>`

.. _SingleRoomSRIR_1.0:

**SingleRoomSRIR v1.0**

For measuring SRIRs in a single room with a single excitation source (e.g., a loudspeaker) and a listener containing an arbitrary number of omnidirectional receivers (e.g., a microphone array).

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 2.1
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SingleRoomSRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - Shall be FIR
   * - GLOBAL_RoomType (*attribute*)
     - shoebox
     - 
     - m
     - Shall be 'shoebox' or 'dae'
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Name of the database. Used for classification of the data.
   * - GLOBAL_RoomShortName (*attribute*)
     - 
     - 
     - 
     - Short name of the Room
   * - GLOBAL_RoomDescription (*attribute*)
     - 
     - 
     - 
     - Informal verbal description of the room
   * - GLOBAL_RoomLocation (*attribute*)
     - 
     - 
     - 
     - Location of the room
   * - GLOBAL_RoomGeometry (*attribute*)
     - 
     - 
     - 
     - URI to a file describing the room geometry.
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ListenerDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ReceiverShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ReceiverDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_SourceShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_SourceDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_EmitterShortName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_EmitterDescription (*attribute*)
     - 
     - 
     - 
     - 
   * - RoomTemperature (*double*)
     - 0
     - I, M
     - 
     - Temperature during measurements, given in Kelvin.
   * - RoomTemperature_Units (*attribute*)
     - kelvin
     - 
     - 
     - Units of the room temperature.
   * - RoomVolume (*double*)
     - 0
     - I, M
     - 
     - Volume of the room.
   * - RoomVolume_Units (*attribute*)
     - cubic metre
     - 
     - 
     - Units of the room volume.
   * - RoomCornerA (*double*)
     - [0, 0, 0]
     - IC, MC
     - 
     - 
   * - RoomCornerB (*double*)
     - [1, 2, 3]
     - IC, MC
     - 
     - 
   * - RoomCorners (*double*)
     - 0
     - II
     - 
     - The value of this attribute is to be ignored. It only exist to for RoomCorners:Type and RoomCorners:Units
   * - RoomCorners_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - RoomCorners_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverDescriptions (*string*)
     - ['']
     - RS, RSM
     - 
     - R-dependent version of the attribute ReceiverDescription
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - IC, RCI, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - spherical
     - 
     - m
     - Can be of any type enabling both spatially discrete and spatially continuous representations.
   * - ReceiverPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - ReceiverView (*double*)
     - [1, 0, 0]
     - RCI, RCM
     - 
     - 
   * - ReceiverUp (*double*)
     - [0, 0, 1]
     - RCI, RCM
     - 
     - 
   * - ReceiverView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - ReceiverView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - EmitterDescriptions (*string*)
     - ['']
     - ES, ESM
     - 
     - E-dependent version of the attribute EmitterDescription
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - spherical
     - 
     - m
     - Shall be 'cartesian' or 'spherical', restricting to spatially discrete emitters.
   * - EmitterPosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterView (*double*)
     - [1, 0, 0]
     - ECI, ECM
     - 
     - 
   * - EmitterUp (*double*)
     - [0, 0, 1]
     - ECI, ECM
     - 
     - 
   * - EmitterView_Type (*attribute*)
     - cartesian
     - 
     - 
     - Shall be 'cartesian' or 'spherical', restricting to spatially discrete emitters.
   * - EmitterView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - MeasurementDate (*double*)
     - 0
     - M
     - 
     - Optional M-dependent date and time of the measurement
   * - Data_IR (*double*)
     - 0
     - mrn
     - m
     - Impulse responses
   * - Data_SamplingRate (*double*)
     - 48000
     - I, M
     - m
     - Sampling rate of the samples in Data.IR and Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the sampling rate
   * - Data_Delay (*double*)
     - 0
     - IR, MR
     - m
     - Additional delay of each IR (in samples)

:ref:`back to top <conventions>`

Deprecated
==========

.. _GeneralFIRE_1.0:

**GeneralFIRE v1.0**

This convention is deprecated. Use :ref:`GeneralFIR-E_2.0 <GeneralFIR-E_2.0>` instead.

This conventions stores IRs for general purposes, i.e., only the mandatory, SOFA general metadata are pre-defined

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - GeneralFIRE
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIRE
     - 
     - r, m
     - We use FIR datatype which in addition depends on Emitters (E)
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - The room information can be arbitrary
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - Each speaker is represented as an emitter. Use EmitterPosition to represent the position of a particular speaker. Size of EmitterPosition determines E
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_IR (*double*)
     - 0
     - mREn
     - m
     - Impulse responses
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - Sampling rate of the samples in Data.IR and Data.Delay
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - Unit of the sampling rate
   * - Data_Delay (*double*)
     - 0
     - IRE, MRE
     - m
     - Additional delay of each IR (in samples)

:ref:`back to top <conventions>`

.. _MultiSpeakerBRIR_0.3:

**MultiSpeakerBRIR v0.3**

This convention is deprecated. Use :ref:`SingleRoomMIMOSRIR_1.0 <SingleRoomMIMOSRIR_1.0>` instead.

This convention is for BRIRs recorded in reverberant conditions from multiple loudspeaker sources at a number of listener orientations.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - MultiSpeakerBRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.3
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIRE
     - 
     - r, m
     - We use FIR datatype which in addition depends on Emitters (E)
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - reverberant
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - GLOBAL_RoomDescription (*attribute*)
     - 
     - 
     - 
     - narrative description of the room
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - Each speaker is represented as an emitter. Use EmitterPosition to represent the position of a particular speaker. Size of EmitterPosition determines E
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - EmitterUp (*double*)
     - [0, 0, 1]
     - ECI, ECM
     - 
     - When EmitterUp provided, EmitterView must be provided as well
   * - EmitterView (*double*)
     - [1, 0, 0]
     - ECI, ECM
     - 
     - When EmitterView provided, EmitterUp must be provided as well
   * - EmitterView_Type (*attribute*)
     - cartesian
     - 
     - 
     - 
   * - EmitterView_Units (*attribute*)
     - metre
     - 
     - 
     - 
   * - Data_IR (*double*)
     - [1, 1]
     - mREn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IRE, MRE
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleFreeFieldHRIR_0.4:

**SimpleFreeFieldHRIR v0.4**

This convention is deprecated. Use :ref:`SimpleFreeFieldHRIR_1.0 <SimpleFreeFieldHRIR_1.0>` instead.

This convention set is for HRIRs recorded under free-field conditions or other IRs created under conditions where room information is irrelevant

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldHRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.4
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, meter
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - Data_IR (*double*)
     - [1, 1]
     - mRn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleFreeFieldTF_0.4:

**SimpleFreeFieldTF v0.4**

This convention is deprecated. Use :ref:`SimpleFreeFieldHRTF_1.0 <SimpleFreeFieldHRTF_1.0>` instead.

This conventions is for TFs created under conditions where room information is irrelevant

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.4
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, meter
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - 
   * - N_LongName (*attribute*)
     - frequency
     - 
     - 
     - 
   * - N_Units (*attribute*)
     - hertz
     - 
     - 
     - 
   * - Data_Real (*double*)
     - [1, 1]
     - mRn
     - m
     - 
   * - Data_Imag (*double*)
     - [0, 0]
     - MRN
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleFreeFieldTF_1.0:

**SimpleFreeFieldTF v1.0**

This convention is deprecated. Use :ref:`SimpleFreeFieldHRTF_1.0 <SimpleFreeFieldHRTF_1.0>` instead.

This conventions is for TFs created under conditions where room information is irrelevant

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleFreeFieldTF
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DataType (*attribute*)
     - TF
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - ID of the subject from the database
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - name of the database to which these data belong
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - Source position is assumed to vary for different directions/positions around the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - N (*double*)
     - 0
     - N
     - m
     - 
   * - N_LongName (*attribute*)
     - frequency
     - 
     - 
     - 
   * - N_Units (*attribute*)
     - hertz
     - 
     - 
     - 
   * - Data_Real (*double*)
     - [0, 0]
     - mRn
     - m
     - 
   * - Data_Imag (*double*)
     - [0, 0]
     - MRN
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleHeadphoneIR_0.1:

**SimpleHeadphoneIR v0.1**

This convention is deprecated. Use :ref:`SimpleHeadphoneIR_1.0 <SimpleHeadphoneIR_1.0>` instead.

Conventions for IRs with a 1-to-1 correspondence between emitter and receiver. The main application for this convention is to store headphone IRs recorded for each emitter and each ear.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleHeadphoneIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.1
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - We will store IRs here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - Room type is not relevant here
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Correspondence to a database
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - Correspondence to a subject from the database
   * - GLOBAL_ListenerDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the listener (or mannequin)
   * - GLOBAL_SourceDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the headphones
   * - GLOBAL_SourceManufacturer (*attribute*)
     - 
     - 
     - m
     - Name of the headphones manufacturer
   * - GLOBAL_SourceModel (*attribute*)
     - 
     - 
     - m
     - Name of the headphone model. Must uniquely describe the headphones of the manufacturer
   * - GLOBAL_SourceURI (*attribute*)
     - 
     - 
     - m
     - URI of the headphone specifications
   * - GLOBAL_ReceiverDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the microphones
   * - GLOBAL_EmitterDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the headphone drivers
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Default: Headphones are located at the position of the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, meter
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - eCI, eCM
     - m
     - Default: Reflects the correspondence of each emitter to each receiver
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - SourceManufacturer (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute SourceManufucturer
   * - SourceModel (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute SourceModel
   * - ReceiverDescription (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute ReceiverDescription
   * - EmitterDescription (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute EmitterDescription
   * - MeasurementDate (*double*)
     - 0
     - M
     - 
     - Optional M-dependent date and time of the measurement
   * - Data_IR (*double*)
     - [1, 1]
     - mRn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

.. _SimpleHeadphoneIR_0.2:

**SimpleHeadphoneIR v0.2**

This convention is deprecated. Use :ref:`SimpleHeadphoneIR_1.0 <SimpleHeadphoneIR_1.0>` instead.

Conventions for IRs with a 1-to-1 correspondence between emitter and receiver. The main application for this convention is to store headphone IRs recorded for each emitter and each ear.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SimpleHeadphoneIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.2
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - We will store IRs here
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - free field
     - 
     - m
     - Room type is not relevant here
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - Correspondence to a database
   * - GLOBAL_ListenerShortName (*attribute*)
     - 
     - 
     - m
     - Correspondence to a subject from the database
   * - GLOBAL_ListenerDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the listener (or mannequin)
   * - GLOBAL_SourceDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the headphones
   * - GLOBAL_SourceManufacturer (*attribute*)
     - 
     - 
     - m
     - Name of the headphones manufacturer
   * - GLOBAL_SourceModel (*attribute*)
     - 
     - 
     - m
     - Name of the headphone model. Must uniquely describe the headphones of the manufacturer
   * - GLOBAL_SourceURI (*attribute*)
     - 
     - 
     - m
     - URI of the headphone specifications
   * - GLOBAL_ReceiverDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the microphones
   * - GLOBAL_EmitterDescription (*attribute*)
     - 
     - 
     - m
     - Narrative description of the headphone drivers
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - Default: Headphones are located at the position of the listener
   * - SourcePosition_Type (*attribute*)
     - spherical
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - degree, degree, metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [[0, 0.09, 0], [0, -0.09, 0]]
     - eCI, eCM
     - m
     - Default: Reflects the correspondence of each emitter to each receiver
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceManufacturer (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute SourceManufucturer
   * - SourceModel (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute SourceModel
   * - ReceiverDescription (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute ReceiverDescription
   * - EmitterDescription (*string*)
     - ['']
     - MS
     - 
     - Optional M-dependent version of the attribute EmitterDescription
   * - MeasurementDate (*double*)
     - 0
     - M
     - 
     - Optional M-dependent date and time of the measurement
   * - Data_IR (*double*)
     - [0, 0]
     - mRn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0, 0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

.. _SingleRoomDRIR_0.2:

**SingleRoomDRIR v0.2**

This convention is deprecated. Use :ref:`SingleRoomSRIR_1.0 <SingleRoomSRIR_1.0>` instead.

This convention stores arbitrary number of receivers while providing an information about the room. The main application is to store DRIRs for a single room.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SingleRoomDRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.2
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - reverberant
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_RoomDescription (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - rCI, rCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - meter
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourceView (*double*)
     - [-1, 0, 0]
     - IC, MC
     - m
     - 
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_IR (*double*)
     - [1]
     - mRn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

.. _SingleRoomDRIR_0.3:

**SingleRoomDRIR v0.3**

This convention is deprecated. Use :ref:`SingleRoomSRIR_1.0 <SingleRoomSRIR_1.0>` instead.

This convention stores arbitrary number of receivers while providing an information about the room. The main application is to store DRIRs for a single room.

.. list-table::
   :widths: 20 50 25 30 100
   :header-rows: 1

   * - Name (Type)
     - Default
     - Dim.
     - Flags
     - Comment
   * - GLOBAL_Conventions (*attribute*)
     - SOFA
     - 
     - r, m
     - 
   * - GLOBAL_Version (*attribute*)
     - 1.0
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventions (*attribute*)
     - SingleRoomDRIR
     - 
     - r, m
     - 
   * - GLOBAL_SOFAConventionsVersion (*attribute*)
     - 0.3
     - 
     - r, m
     - 
   * - GLOBAL_APIName (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_APIVersion (*attribute*)
     - 
     - 
     - r, m
     - 
   * - GLOBAL_ApplicationName (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_ApplicationVersion (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_AuthorContact (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Comment (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DataType (*attribute*)
     - FIR
     - 
     - r, m
     - 
   * - GLOBAL_History (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_License (*attribute*)
     - No license provided, ask the author for permission
     - 
     - m
     - 
   * - GLOBAL_Organization (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_References (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_RoomType (*attribute*)
     - reverberant
     - 
     - m
     - 
   * - GLOBAL_Origin (*attribute*)
     - 
     - 
     - 
     - 
   * - GLOBAL_DateCreated (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DateModified (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_Title (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_DatabaseName (*attribute*)
     - 
     - 
     - m
     - 
   * - GLOBAL_RoomDescription (*attribute*)
     - 
     - 
     - m
     - 
   * - ListenerPosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ReceiverPosition (*double*)
     - [0, 0, 0]
     - RCI, RCM
     - m
     - 
   * - ReceiverPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ReceiverPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourcePosition (*double*)
     - [0, 0, 0]
     - IC, MC
     - m
     - 
   * - SourcePosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourcePosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - EmitterPosition (*double*)
     - [0, 0, 0]
     - eCI, eCM
     - m
     - 
   * - EmitterPosition_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - EmitterPosition_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - ListenerUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - ListenerView (*double*)
     - [1, 0, 0]
     - IC, MC
     - m
     - 
   * - ListenerView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - ListenerView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - SourceUp (*double*)
     - [0, 0, 1]
     - IC, MC
     - m
     - 
   * - SourceView (*double*)
     - [-1, 0, 0]
     - IC, MC
     - m
     - 
   * - SourceView_Type (*attribute*)
     - cartesian
     - 
     - m
     - 
   * - SourceView_Units (*attribute*)
     - metre
     - 
     - m
     - 
   * - Data_IR (*double*)
     - [0]
     - mrn
     - m
     - 
   * - Data_SamplingRate (*double*)
     - 48000
     - I
     - m
     - 
   * - Data_SamplingRate_Units (*attribute*)
     - hertz
     - 
     - m
     - 
   * - Data_Delay (*double*)
     - [0]
     - IR, MR
     - m
     - 

:ref:`back to top <conventions>`

