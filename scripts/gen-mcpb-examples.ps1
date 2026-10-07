#Requires -Version 5.1
<#
  gen-mcpb-examples.ps1 — build assets/prompts/examples.json (MCPB 3-4-100 gate).

  Emits 100+ hand-authored tool-call examples (tool + action + realistic
  arguments + description) matching the live portmanteau signatures.
  Re-run after signature changes and diff the result.
#>
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $RepoRoot 'assets\prompts\examples.json'

$examples = @(
  # resolve_project (10)
  @{tool='resolve_project'; action='create'; arguments=@{name='Summer Ad'; frame_rate=24.0; width=3840; height=2160}; description='Create a 4K project'}
  @{tool='resolve_project'; action='create'; arguments=@{name='Podcast Ep 12'; frame_rate=30.0; width=1920; height=1080}; description='Create a 1080p30 project'}
  @{tool='resolve_project'; action='open'; arguments=@{name='Summer Ad'}; description='Open an existing project'}
  @{tool='resolve_project'; action='open'; arguments=@{name='Client Video'}; description='Open another project'}
  @{tool='resolve_project'; action='list'; arguments=@{}; description='List all projects'}
  @{tool='resolve_project'; action='list'; arguments=@{}; description='List projects again after creating one'}
  @{tool='resolve_project'; action='get_settings'; arguments=@{}; description='Read current project settings'}
  @{tool='resolve_project'; action='get_settings'; arguments=@{}; description='Read settings before changing frame rate'}
  @{tool='resolve_project'; action='update_settings'; arguments=@{settings=@{timelineFrameRate='30.0'}}; description='Set timeline frame rate'}
  @{tool='resolve_project'; action='update_settings'; arguments=@{settings=@{timelineResolutionWidth='1280'; timelineResolutionHeight='720'}}; description='Downscale timeline resolution'}
  # resolve_media (8)
  @{tool='resolve_media'; action='import'; arguments=@{paths=@('C:/Footage/a001.mp4', 'C:/Footage/a002.mp4')}; description='Import two clips'}
  @{tool='resolve_media'; action='import'; arguments=@{paths=@('C:/Footage/raw.mp4'); target_folder='Raw Footage'}; description='Import into a folder'}
  @{tool='resolve_media'; action='list'; arguments=@{folder_path='Raw Footage'}; description='List a folder'}
  @{tool='resolve_media'; action='list'; arguments=@{}; description='List media pool root'}
  @{tool='resolve_media'; action='create_folder'; arguments=@{folder_path='Assets/Music'}; description='Create a folder'}
  @{tool='resolve_media'; action='create_folder'; arguments=@{folder_path='Parent/Child'}; description='Create nested folders'}
  @{tool='resolve_media'; action='get_metadata'; arguments=@{clip_path='C:/Footage/a001.mp4'}; description='Read clip metadata by path'}
  @{tool='resolve_media'; action='get_metadata'; arguments=@{clip_path='a001.mp4'}; description='Read clip metadata by name'}
  # resolve_timeline (24)
  @{tool='resolve_timeline'; action='create'; arguments=@{name='Main Edit'; width=3840; height=2160}; description='Create 4K timeline'}
  @{tool='resolve_timeline'; action='create'; arguments=@{name='Selects'; frame_rate=25.0}; description='Create PAL timeline'}
  @{tool='resolve_timeline'; action='info'; arguments=@{}; description='Describe current timeline'}
  @{tool='resolve_timeline'; action='info'; arguments=@{timeline_name='Main Edit'}; description='Describe a named timeline'}
  @{tool='resolve_timeline'; action='add_clip'; arguments=@{clip_path='C:/Footage/a001.mp4'}; description='Add clip to video track 1'}
  @{tool='resolve_timeline'; action='add_clip'; arguments=@{clip_path='C:/Audio/vo.wav'; track_index=1; track_type='audio'}; description='Add voiceover to audio track 1'}
  @{tool='resolve_timeline'; action='cut'; arguments=@{frame=240; track_index=1}; description='Cut at frame 240'}
  @{tool='resolve_timeline'; action='cut'; arguments=@{frame=48; track_index=2; track_type='audio'}; description='Cut audio at frame 48'}
  @{tool='resolve_timeline'; action='set_playhead'; arguments=@{frame=120}; description='Move playhead'}
  @{tool='resolve_timeline'; action='set_playhead'; arguments=@{frame=0}; description='Park playhead at start'}
  @{tool='resolve_timeline'; action='add_marker'; arguments=@{frame=120; color='Red'; name='VFX cue'}; description='Add red marker'}
  @{tool='resolve_timeline'; action='add_marker'; arguments=@{frame=48; color='Green'; note='Good take'}; description='Add green marker with note'}
  @{tool='resolve_timeline'; action='get_markers'; arguments=@{}; description='List markers'}
  @{tool='resolve_timeline'; action='get_markers'; arguments=@{timeline_name='Main Edit'}; description='List markers on named timeline'}
  @{tool='resolve_timeline'; action='delete_marker'; arguments=@{frame=120}; description='Delete marker'}
  @{tool='resolve_timeline'; action='delete_marker'; arguments=@{frame=48}; description='Delete another marker'}
  @{tool='resolve_timeline'; action='add_keyframe'; arguments=@{property_name='Zoom'; frame=0; value=1.0}; description='Add zoom keyframe'}
  @{tool='resolve_timeline'; action='add_keyframe'; arguments=@{property_name='Opacity'; frame=24; value=0.5}; description='Add opacity keyframe'}
  @{tool='resolve_timeline'; action='get_keyframes'; arguments=@{property_name='Zoom'}; description='List zoom keyframes'}
  @{tool='resolve_timeline'; action='get_keyframes'; arguments=@{property_name='Speed'}; description='List speed keyframes'}
  @{tool='resolve_timeline'; action='delete_keyframe'; arguments=@{property_name='Zoom'; frame=0}; description='Delete keyframe'}
  @{tool='resolve_timeline'; action='delete_keyframe'; arguments=@{property_name='Opacity'; frame=24}; description='Delete opacity keyframe'}
  @{tool='resolve_timeline'; action='set_clip_property'; arguments=@{property_name='Speed'; value=2.0}; description='Double clip speed'}
  @{tool='resolve_timeline'; action='set_clip_property'; arguments=@{property_name='Zoom'; value=1.5}; description='Punch in 150 percent'}
  # resolve_color (14)
  @{tool='resolve_color'; action='create_node'; arguments=@{node_type='primary'; node_name='Base Grade'}; description='Create primary node'}
  @{tool='resolve_color'; action='create_node'; arguments=@{node_type='curves'; node_name='Contrast'}; description='Create curves node'}
  @{tool='resolve_color'; action='apply_lut'; arguments=@{clip_path='C:/Footage/a001.mp4'; lut_path='C:/LUTs/Film.cube'}; description='Apply LUT full strength'}
  @{tool='resolve_color'; action='apply_lut'; arguments=@{clip_path='C:/Footage/a001.mp4'; lut_path='C:/LUTs/Film.cube'; intensity=0.8}; description='Apply LUT at 80 percent'}
  @{tool='resolve_color'; action='set_color_space'; arguments=@{input_color_space='Rec.709'; output_color_space='DaVinci Wide Gamut'}; description='Wide gamut transform'}
  @{tool='resolve_color'; action='set_color_space'; arguments=@{input_color_space='Rec.709'; output_color_space='Rec.709'; input_gamma='Rec.709'; output_gamma='sRGB'}; description='Gamma-only transform'}
  @{tool='resolve_color'; action='adjust_wheels'; arguments=@{lift=@{r=0.1; g=0.0; b=-0.1}}; description='Cool the shadows'}
  @{tool='resolve_color'; action='adjust_wheels'; arguments=@{gain=@{r=0.05; g=0.05; b=0.05}}; description='Warm the highlights'}
  @{tool='resolve_color'; action='grab_still'; arguments=@{}; description='Checkpoint current grade'}
  @{tool='resolve_color'; action='grab_still'; arguments=@{still_name='Approved v1'}; description='Named checkpoint'}
  @{tool='resolve_color'; action='get_stills'; arguments=@{}; description='List gallery stills'}
  @{tool='resolve_color'; action='get_stills'; arguments=@{}; description='List stills before matching'}
  @{tool='resolve_color'; action='apply_grade_from_still'; arguments=@{still_index=0}; description='Apply grade from still 0'}
  @{tool='resolve_color'; action='apply_grade_from_still'; arguments=@{still_index=2}; description='Apply grade from still 2'}
  # resolve_render (8)
  @{tool='resolve_render'; action='timeline'; arguments=@{output_path='C:/Output'; format='mp4'}; description='Render MP4'}
  @{tool='resolve_render'; action='timeline'; arguments=@{output_path='C:/Output'; format='prores'; resolution='3840x2160'; codec='prores_422_hq'}; description='Render 4K ProRes master'}
  @{tool='resolve_render'; action='presets'; arguments=@{}; description='List render presets'}
  @{tool='resolve_render'; action='presets'; arguments=@{}; description='List presets before delivery'}
  @{tool='resolve_render'; action='with_preset'; arguments=@{preset_name='YouTube 4K'; output_path='C:/Output'}; description='Render with preset'}
  @{tool='resolve_render'; action='with_preset'; arguments=@{preset_name='Vimeo 1080p'; output_path='C:/Output'}; description='Render Vimeo version'}
  @{tool='resolve_render'; action='job_status'; arguments=@{job_id=1}; description='Check job 1'}
  @{tool='resolve_render'; action='job_status'; arguments=@{job_id=2}; description='Check job 2'}
  # resolve_audio (8)
  @{tool='resolve_audio'; action='get_tracks'; arguments=@{}; description='List audio tracks'}
  @{tool='resolve_audio'; action='get_tracks'; arguments=@{timeline_name='Main Edit'}; description='List tracks on named timeline'}
  @{tool='resolve_audio'; action='add_effect'; arguments=@{track_index=1; effect_type='eq'}; description='Add EQ'}
  @{tool='resolve_audio'; action='add_effect'; arguments=@{track_index=2; effect_type='compressor'}; description='Add compressor'}
  @{tool='resolve_audio'; action='adjust_levels'; arguments=@{track_index=1; volume=0.8; pan=-0.5}; description='Set level and pan'}
  @{tool='resolve_audio'; action='adjust_levels'; arguments=@{track_index=2; mute=$true}; description='Mute track 2'}
  @{tool='resolve_audio'; action='normalize'; arguments=@{target_level=-23.0}; description='Normalize to broadcast'}
  @{tool='resolve_audio'; action='normalize'; arguments=@{track_indices=@(1, 2, 3)}; description='Normalize first three tracks'}
  # resolve_fairlight (18)
  @{tool='resolve_fairlight'; operation='open_page'; arguments=@{}; description='Switch to Fairlight page'}
  @{tool='resolve_fairlight'; operation='open_page'; arguments=@{}; description='Open Fairlight before mixing'}
  @{tool='resolve_fairlight'; operation='get_tracks'; arguments=@{}; description='List Fairlight tracks'}
  @{tool='resolve_fairlight'; operation='get_tracks'; arguments=@{timeline_name='Main Edit'}; description='List tracks on named timeline'}
  @{tool='resolve_fairlight'; operation='set_mute'; arguments=@{track_index=2; mute=$true}; description='Mute track 2'}
  @{tool='resolve_fairlight'; operation='set_mute'; arguments=@{track_index=2; mute=$false}; description='Unmute track 2'}
  @{tool='resolve_fairlight'; operation='set_solo'; arguments=@{track_index=1; solo=$true}; description='Solo dialogue'}
  @{tool='resolve_fairlight'; operation='set_solo'; arguments=@{track_index=1; solo=$false}; description='Unsolo dialogue'}
  @{tool='resolve_fairlight'; operation='set_volume'; arguments=@{track_index=1; volume=0.8}; description='Set dialogue level'}
  @{tool='resolve_fairlight'; operation='set_volume'; arguments=@{track_index=3; volume=0.5}; description='Set music bed level'}
  @{tool='resolve_fairlight'; operation='track_eq'; arguments=@{track_index=1; eq_band=1; eq_gain_db=-3.5}; description='Cut band 1'}
  @{tool='resolve_fairlight'; operation='track_eq'; arguments=@{track_index=1}; description='Read EQ state'}
  @{tool='resolve_fairlight'; operation='track_send'; arguments=@{track_index=1; bus_index=1; send_level=0.75}; description='Send to bus 1'}
  @{tool='resolve_fairlight'; operation='track_send'; arguments=@{track_index=2; bus_index=1; send_level=0.5; send_pre_fader=$true}; description='Pre-fader send'}
  @{tool='resolve_fairlight'; operation='get_buses'; arguments=@{}; description='Show bus configuration'}
  @{tool='resolve_fairlight'; operation='get_buses'; arguments=@{timeline_name='Main Edit'}; description='Show buses for timeline'}
  @{tool='resolve_fairlight'; operation='track_automation'; arguments=@{track_index=1}; description='Read volume automation'}
  @{tool='resolve_fairlight'; operation='track_automation'; arguments=@{track_index=1; automation_param='pan'}; description='Read pan automation'}
  # resolve_subtitle (12)
  @{tool='resolve_subtitle'; action='add'; arguments=@{name='Intro'; start_frame=0; end_frame=48; text='Hello'}; description='Add opening caption'}
  @{tool='resolve_subtitle'; action='add'; arguments=@{name='Outro'; start_frame=2400; end_frame=2448; text='Thanks'}; description='Add closing caption'}
  @{tool='resolve_subtitle'; action='get'; arguments=@{track_index=1}; description='List track 1 captions'}
  @{tool='resolve_subtitle'; action='get'; arguments=@{track_index=2}; description='List track 2 captions'}
  @{tool='resolve_subtitle'; action='edit'; arguments=@{subtitle_index=0; text='Welcome back'}; description='Fix caption text'}
  @{tool='resolve_subtitle'; action='edit'; arguments=@{subtitle_index=1; start_frame=100; end_frame=148}; description='Retimime caption'}
  @{tool='resolve_subtitle'; action='delete'; arguments=@{subtitle_index=2}; description='Delete caption 2'}
  @{tool='resolve_subtitle'; action='delete'; arguments=@{subtitle_index=0}; description='Delete first caption'}
  @{tool='resolve_subtitle'; action='import_srt'; arguments=@{srt_path='C:/captions.srt'}; description='Import SRT file'}
  @{tool='resolve_subtitle'; action='import_srt'; arguments=@{srt_path='C:/captions.srt'; track_index=2}; description='Import SRT to track 2'}
  @{tool='resolve_subtitle'; action='export_srt'; arguments=@{output_path='C:/delivery/captions.srt'}; description='Export delivery SRT'}
  @{tool='resolve_subtitle'; action='export_srt'; arguments=@{output_path='C:/delivery/captions.srt'; track_index=1}; description='Export track 1 SRT'}
  # resolve_system (12)
  @{tool='resolve_system'; action='info'; arguments=@{}; description='Resolve version and connection'}
  @{tool='resolve_system'; action='info'; arguments=@{}; description='Version check before delivery'}
  @{tool='resolve_system'; action='status'; arguments=@{}; description='Server and connection status'}
  @{tool='resolve_system'; action='status'; arguments=@{}; description='Status check after reconnect'}
  @{tool='resolve_system'; action='health'; arguments=@{}; description='Full health check'}
  @{tool='resolve_system'; action='health'; arguments=@{}; description='Health check before batch'}
  @{tool='resolve_system'; action='help'; arguments=@{}; description='General help'}
  @{tool='resolve_system'; action='help'; arguments=@{topic='color_grading'; level='beginner'}; description='Beginner color help'}
  @{tool='resolve_system'; action='host_status'; arguments=@{}; description='Host lifecycle probe'}
  @{tool='resolve_system'; action='host_status'; arguments=@{}; description='Probe when disconnected'}
  @{tool='resolve_system'; action='host_launch'; arguments=@{}; description='Launch installed Resolve'}
  @{tool='resolve_system'; action='host_launch'; arguments=@{}; description='Launch before morning batch'}
)

$items = foreach ($i in 0..($examples.Count - 1)) {
  $e = $examples[$i]
  $verb = if ($e.ContainsKey('operation')) { $e.operation } else { $e.action }
  $args = [ordered]@{}
  foreach ($k in $e.arguments.Keys) { $args[$k] = $e.arguments[$k] }
  if ($e.ContainsKey('operation')) { $args['operation'] = $e.operation } else { $args['action'] = $e.action }
  $slug = ("{0}-{1}-{2}" -f $e.tool, $verb, ($i + 1)).ToLower() -replace '[^a-z0-9]+', '-'
  # Standard shape per MCPB_PACKAGING_STANDARDS 2.3b:
  # {name, description, prompt, tool, arguments}
  [ordered]@{
    name = $slug.Trim('-')
    description = "$($e.tool).$($verb): $($e.description)"
    prompt = $e.description
    tool = $e.tool
    arguments = $args
  }
}

New-Item -ItemType Directory -Force -Path (Split-Path $Out) | Out-Null
$json = $items | ConvertTo-Json -Depth 6
# UTF-8 without BOM (Windows PowerShell 5.1 has no UTF8NoBOM enum value)
[System.IO.File]::WriteAllText($Out, $json, [System.Text.UTF8Encoding]::new($false))
Write-Host "Wrote $($items.Count) examples to $Out"
