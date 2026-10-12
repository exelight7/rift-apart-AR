# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import json,re,textwrap
R=Path(__file__).resolve().parents[1]
# Editorial replacements are written explicitly in logical Arabic.
DATA='''
PCDISPLAYSETTINGS_ASPECTRATIO_DESC|يضبط نسبة أبعاد الصورة لتناسب العرض المطلوب مقارنة بنسبة أبعاد شاشتك.
PCDISPLAYSETTINGS_BRIGHTNESS_DESC|اضبط سطوع الصورة. القيمة 0 هي الأغمق، والقيمة 100 هي الأكثر سطوعًا.
PCDISPLAYSETTINGS_CONTRAST_DESC|اضبط تباين الصورة. القيمة 0 هي الأدنى، والقيمة 10 هي الأعلى.
PCDISPLAYSETTINGS_DISPLAYRESOLUTION_DESC|يحدد دقة عرض اللعبة.
PCDISPLAYSETTINGS_DLSS|NVIDIA DLSS
PCDISPLAYSETTINGS_DLSSG|توليد الإطارات بتقنية DLSS
PCDISPLAYSETTINGS_DLSSG_DESC|تستخدم تقنية DLSS الذكاء الاصطناعي لتوليد إطارات إضافية. يتطلب هذا الخيار بطاقة رسوميات متوافقة من سلسلة GeForce RTX 40.
PCDISPLAYSETTINGS_DRS|الدقة الديناميكية
PCDISPLAYSETTINGS_DRS_DESC|حدد معدل الإطارات المستهدف. تضبط اللعبة دقة العرض الداخلية تلقائيًا للحفاظ على هذا المعدل بأفضل جودة ممكنة. لا تُحتسب الإطارات المولدة ضمن المعدل المستهدف.
PCDISPLAYSETTINGS_EXCLUSIVEFULLSCREEN|ملء الشاشة الحصري
PCDISPLAYSETTINGS_FRAMEGEN_DESC|يولد إطارات إضافية بالاعتماد على بيانات الإطارات السابقة. يتطلب توليد الإطارات بتقنية DLSS بطاقة رسوميات متوافقة من سلسلة GeForce RTX 40.
PCDISPLAYSETTINGS_FSR|AMD FSR 3
PCDISPLAYSETTINGS_FSRAA|AMD FSR 3 Native AA
PCDISPLAYSETTINGS_FSRFRAMEGEN|توليد الإطارات بتقنية FSR 3
PCDISPLAYSETTINGS_HDR|HDR
PCDISPLAYSETTINGS_HDRMAXNITS|أقصى سطوع HDR
PCDISPLAYSETTINGS_HDRMAXNITS_DESC|اضبط أقصى سطوع للصورة في وضع HDR. يُقاس السطوع بوحدة النيت.
PCDISPLAYSETTINGS_HDRPAPERWHITE|سطوع الأبيض في HDR
PCDISPLAYSETTINGS_HDRPAPERWHITE_DESC|اضبط السطوع الأساسي للمناطق البيضاء في وضع HDR. يُقاس السطوع بوحدة النيت.
PCDISPLAYSETTINGS_HDR_DESC|يبدل بين عرض HDR وعرض SDR. لا يتاح هذا الخيار إلا عند تفعيل HDR في إعدادات Windows.
PCDISPLAYSETTINGS_IGTI|IGTI
PCDISPLAYSETTINGS_MONITOR_DESC|اختر الشاشة التي تريد عرض اللعبة عليها.
PCDISPLAYSETTINGS_NVIDIAREFLEX|NVIDIA Reflex
PCDISPLAYSETTINGS_NVIDIAREFLEX_DESC|يقلل زمن استجابة النظام. يحاول وضع التعزيز تقليل التأخير بصورة إضافية لتحسين الاستجابة.
PCDISPLAYSETTINGS_ONPLUSBOOST|مفعل مع التعزيز
PCDISPLAYSETTINGS_REFRESHRATE_DESC|يحدد معدل تحديث الشاشة. يمكن تغييره عند استخدام وضع ملء الشاشة الحصري فقط.
PCDISPLAYSETTINGS_UPSCALEMETHOD|طريقة رفع الدقة
PCDISPLAYSETTINGS_UPSCALEMETHOD_DESC|اختر تقنية تنعيم الحواف ورفع الدقة لتحسين جودة الصورة والأداء. اضبط مستوى الجودة ومعدل الإطارات المستهدف من الخيارات أدناه.
PCDISPLAYSETTINGS_UPSCALEQUALITY|جودة رفع الدقة
PCDISPLAYSETTINGS_UPSCALEQUALITY_DESC|اختر مستوى جودة رفع الدقة. تستخدم خيارات الجودة دقة داخلية أعلى، بينما تستخدم خيارات الأداء دقة أقل لزيادة معدل الإطارات. يتغير الخيار إلى ديناميكي عند تحديد معدل مستهدف للدقة الديناميكية.
PCDISPLAYSETTINGS_UPSCALESHARPNESS|حدة الصورة
PCDISPLAYSETTINGS_UPSCALESHARPNESS_DESC|اضبط حدة الصورة الناتجة عن تقنية رفع الدقة المحددة.
PCDISPLAYSETTINGS_VSYNC_DESC|يزامن عرض الإطارات مع تحديث الشاشة لمنع تمزق الصورة.
PCDISPLAYSETTINGS_WINDOWMODE_DESC|اختر وضع النافذة أو ملء الشاشة أو ملء الشاشة الحصري.
PCDISPLAYSETTINGS_XESS|Intel XeSS
PCGRAPHICSSETTINGS_16XANISOTROPIC|ترشيح متباين الخواص ×16
PCGRAPHICSSETTINGS_2XANISOTROPIC|ترشيح متباين الخواص ×2
PCGRAPHICSSETTINGS_4XANISOTROPIC|ترشيح متباين الخواص ×4
PCGRAPHICSSETTINGS_8XANISOTROPIC|ترشيح متباين الخواص ×8
PCGRAPHICSSETTINGS_AO|التظليل المحيطي
PCGRAPHICSSETTINGS_AO_DESC|يضيف ظلالًا إلى الشقوق والزوايا لإبراز العمق في المشهد.
PCGRAPHICSSETTINGS_BLOOM_DESC|يضيف توهجًا حول المناطق الساطعة في الصورة.
PCGRAPHICSSETTINGS_CHROMATICABERRATION_DESC|يحاكي انحراف الألوان الناتج عن عدسات الكاميرا.
PCGRAPHICSSETTINGS_CROWDDENSITY|كثافة الحشود
PCGRAPHICSSETTINGS_CROWDDENSITY_DESC|اضبط عدد المارة في المدينة. قد تحسن القيم المنخفضة أداء المعالج وبطاقة الرسوميات. تظهر التغييرات تدريجيًا أثناء التنقل.
PCGRAPHICSSETTINGS_DEPTHOFFIELD_DESC|يحاكي تركيز عدسة الكاميرا بجعل أجزاء من المشهد واضحة وتمويه الأجزاء الأخرى.
PCGRAPHICSSETTINGS_DLAA|NVIDIA DLAA
PCGRAPHICSSETTINGS_FILMGRAINSTRENGTH|شدة التحبب السينمائي
PCGRAPHICSSETTINGS_FILMGRAINSTRENGTH_DESC|اضبط شدة التحبب الذي يحاكي مظهر الأفلام السينمائية.
PCGRAPHICSSETTINGS_FOVCORRECTION_DESC|زد زاوية رؤية الكاميرا أو قللها بالنسبة المحددة.
PCGRAPHICSSETTINGS_FULLSCREENEFFECTS_DESC|يفعل مؤثرات الشاشة مثل وهج العدسة والتموج الحراري وقطرات المطر وتأثيرات الغاز، أو يعطلها.
PCGRAPHICSSETTINGS_GEOMETRYDETAIL|تفاصيل مجسمات الانعكاسات
PCGRAPHICSSETTINGS_GEOMETRYDETAIL_DESC|يستخدم مجسمات أعلى تفصيلًا للعناصر القريبة عند تتبع الأشعة، لإظهار انعكاسات أكثر واقعية.
PCGRAPHICSSETTINGS_HAIRQUALITY_DESC|اضبط كثافة شعر الشخصيات وتفاصيل انحنائه.
PCGRAPHICSSETTINGS_HBAOPLUS|HBAO+
PCGRAPHICSSETTINGS_LENSFLARES_DESC|يحاكي الوهج والتشتت الناتجين عن مرور الضوء الساطع عبر عدسة الكاميرا.
PCGRAPHICSSETTINGS_LEVELOFDETAIL_DESC|تزيد الجودة الأعلى مسافة عرض المجسمات بتفاصيلها الكاملة. تقلل الجودة المنخفضة هذه المسافة لتحسين أداء المعالج وبطاقة الرسوميات.
PCGRAPHICSSETTINGS_MOTIONBLUR|شدة ضبابية الحركة
PCGRAPHICSSETTINGS_MOTIONBLUR_DESC|يموه الأجسام في اتجاه حركتها ليجعل الحركة تبدو أكثر سلاسة.
PCGRAPHICSSETTINGS_OBJECTRANGE|مدى تتبع الأجسام
PCGRAPHICSSETTINGS_OBJECTRANGE_DESC|اضبط مدى الأجسام المشمولة في حسابات تتبع الأشعة. تقلل القيم المنخفضة حمل هذه الحسابات على المعالج.
PCGRAPHICSSETTINGS_PARTICLELIGHTING_DESC|اضبط جودة مؤثرات جسيمات الطقس في اللعبة.
PCGRAPHICSSETTINGS_PHANTOMDASHEFFECT_DESC|يفعل الأثر البصري المصاحب لاندفاعة الطيف، أو يعطله.
PCGRAPHICSSETTINGS_PRESET|إعدادات مسبقة
PCGRAPHICSSETTINGS_PRESET_DESC|اختر مجموعة إعدادات رسومية جاهزة تناسب مستوى الأداء المطلوب.
PCGRAPHICSSETTINGS_RAYTRACING_DESC|يفعل تتبع الأشعة.
PCGRAPHICSSETTINGS_REFLECTIONRESOLUTION|دقة الانعكاسات
PCGRAPHICSSETTINGS_REFLECTIONRESOLUTION_DESC|اضبط عدد الأشعة المستخدمة لرسم الانعكاسات. قد يقلل الخيار عالي جدًا معدل الإطارات، خصوصًا عند استخدام دقة عرض مرتفعة.
PCGRAPHICSSETTINGS_RTAO|RTAO
PCGRAPHICSSETTINGS_RT_AMBIENTOCCLUSION|التظليل المحيطي بتتبع الأشعة
PCGRAPHICSSETTINGS_RT_AMBIENTOCCLUSION_DESC|يستخدم تتبع الأشعة لإضافة ظلال واقعية إلى الشقوق والزوايا وإبراز عمق المشهد.
PCGRAPHICSSETTINGS_RT_REFLECTIONS_DESC|يستخدم تتبع الأشعة لعرض انعكاسات واقعية تشمل الأجسام المتحركة والأجسام خارج الشاشة. قد يؤثر بشدة في الأداء عند رفع الجودة.
PCGRAPHICSSETTINGS_RT_SHADOWS_DESC|يستخدم تتبع الأشعة لإظهار ظلال الشمس بصورة أكثر واقعية وتفصيلًا.
PCGRAPHICSSETTINGS_SCREENSHAKE_DESC|يفعل اهتزاز الشاشة أثناء اللعب، أو يعطله.
PCGRAPHICSSETTINGS_SCREENSPACEREFLECTIONS|انعكاسات حيز الشاشة
PCGRAPHICSSETTINGS_SCREENSPACEREFLECTIONS_DESC|يفعل الانعكاسات المعتمدة على العناصر الظاهرة في الشاشة، أو يعطلها.
PCGRAPHICSSETTINGS_SHADOWQUALITY_DESC|تزيد الجودة الأعلى تفاصيل الظلال، بينما تقلل الجودة المنخفضة الحمل على بطاقة الرسوميات.
PCGRAPHICSSETTINGS_SHARPNESS_DESC|اضبط حدة الصورة. تزيد القيم الأعلى وضوح التفاصيل.
PCGRAPHICSSETTINGS_SMAA|SMAA
PCGRAPHICSSETTINGS_SSAA|تنعيم الحواف
PCGRAPHICSSETTINGS_SSAA_DESC|يحدد تقنية تنعيم حواف المجسمات.
PCGRAPHICSSETTINGS_SSAO|SSAO
PCGRAPHICSSETTINGS_TAA|TAA
PCGRAPHICSSETTINGS_TESSELLATION_DESC|يضيف تفاصيل هندسية إلى أسطح المجسمات القريبة.
PCGRAPHICSSETTINGS_TEXTUREFILTERING|ترشيح الخامات
PCGRAPHICSSETTINGS_TEXTUREFILTERING_DESC|تحسن الجودة الأعلى وضوح الخامات عند النظر إليها بزاوية، بينما تحسن الجودة المنخفضة أداء بطاقة الرسوميات.
PCGRAPHICSSETTINGS_TEXTUREQUALITY|جودة الخامات
PCGRAPHICSSETTINGS_TEXTUREQUALITY_DESC|تستخدم الجودة الأعلى ذاكرة أكبر لعرض خامات أكثر تفصيلًا.
PCGRAPHICSSETTINGS_TRAFFICDENSITY_DESC|اضبط عدد المركبات في المدينة. قد تقلل القيم المنخفضة حمل المعالج. تظهر التغييرات تدريجيًا أثناء التنقل.
PCGRAPHICSSETTINGS_TRILINEAR|ترشيح ثلاثي الخطية
PCGRAPHICSSETTINGS_VIGNETTE_DESC|يضيف تظليلًا إلى حواف الصورة لمحاكاة عدسة الكاميرا.
PCGRAPHICSSETTINGS_XEAA|XeSS Native AA
PCGRAPHICSSETTINGS_XEGTAO|XeGTAO
SETTINGS_CONNECTIONS_HEADER|إدارة الحسابات المرتبطة.
SETTINGS_CONNECTIONS_TAB|ربط الحسابات
SETTINGS_DISPLAY_GRAPHICS_DESC|اضبط إعدادات الشاشة والرسوميات والأداء.
SETTINGS_DISPLAY_GRAPHICS_HEADER|إعدادات الشاشة والرسوميات
SETTINGS_DISPLAY_GRAPHICS_TAB|الشاشة والرسوميات
SETTINGS_KEY_BINDING_HEADER|خصص أزرار لوحة المفاتيح والفأرة.
SETTING_CLOSE_GAME_BODY|لن تسري التغييرات على هذا الخيار إلا بعد إغلاق اللعبة وتشغيلها مجددًا.
SETTING_RELOAD_CONFIRM_BODY|يتطلب تغيير هذا الإعداد إعادة اللعب من آخر نقطة حفظ.
SETTING_RELOAD_CONFIRM_HEADER|إعادة اللعب من آخر نقطة حفظ؟
SETTING_RELOAD_LOBBY_BODY|يتطلب تغيير هذا الإعداد إعادة تحميل القائمة الرئيسية.
SETTING_RELOAD_LOBBY_HEADER|إعادة التحميل؟
AUDIO_CONTROLLER_AUDIOHAPTICS_ENABLED_DESC|يفعل ردود الفعل اللمسية المتقدمة في جهاز التحكم اللاسلكي. عند تعطيله، يستخدم الاهتزاز التقليدي.
AUDIO_CONTROLLER_AUDIOHAPTICS_ENABLED_TITLE|ردود الفعل اللمسية المتقدمة
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_AUTO_DESC|يوجه الصوت إلى سماعة الرأس عند توصيلها، وإلى مكبر الصوت في غير ذلك.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_DESC|يحدد مخرج الصوت في جهاز التحكم اللاسلكي.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_HEADSETMONO_DESC|يشغل صوت جهاز التحكم عبر سماعة الرأس بصوت أحادي.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_HEADSETMONO_TITLE|سماعة الرأس — أحادي
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_HEADSETSPEAKER_DESC|يشغل صوت جهاز التحكم عبر سماعة الرأس ومكبر الصوت معًا.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_HEADSET_DESC|يشغل صوت جهاز التحكم عبر سماعة الرأس بصوت ستيريو.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_HEADSET_TITLE|سماعة الرأس — ستيريو
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_OFF_DESC|يعطل إخراج الصوت عبر جهاز التحكم.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_SPEAKER_DESC|يشغل صوت جهاز التحكم عبر مكبر الصوت.
AUDIO_CONTROLLER_SCEPAD_AUDIOMODE_TITLE|مخرج صوت جهاز التحكم
PAUSE_OPTION_CONTROLLERLAYOUT_DESC|اعرض توزيع أزرار جهاز التحكم وخصص وظائفها.
PAUSE_OPTION_CONTROLLERLAYOUT_DESC_ALT|اعرض توزيع أزرار جهاز التحكم.
PAUSE_OPTION_CONTROLLERLAYOUT_TITLE|توزيع أزرار جهاز التحكم
PAUSE_OPTION_MANUALSAVE_DESC|احفظ تقدمك يدويًا.
PAUSE_OPTION_PHOTO_MODE_DESC|ادخل وضع التصوير. يمكنك تعيين اختصار له من الإعدادات، ثم التحكم والاختصارات.
PAUSE_OPTION_PHOTO_MODE_DESC_PC|ادخل وضع التصوير. يمكنك تعيين اختصار له من الإعدادات، ثم الفأرة ولوحة المفاتيح، ثم الاختصارات وسرعة اللعبة.
PAUSE_OPTION_QUIT_DESC|أنه جلسة اللعب.
PAUSE_OPTION_RESTART_DESC|أعد اللعب من آخر نقطة حفظ.
PAUSE_OPTION_RESTART_TITLE|العودة إلى آخر نقطة حفظ
PAUSE_OPTION_RESUME_DESC|أكد الإعدادات واستأنف اللعب.
PAUSE_OPTION_SETTINGS_DESC|اضبط إعدادات اللعبة.
PAUSE_OPTION_SKIPCINE_DESC|تخط المشهد السينمائي الحالي.
PAUSE_OPTION_SKIPGLITCH_DESC|أكمل تحدي جليتش الحالي تلقائيًا وعد إلى راتشت.
PAUSE_OPTION_SKIPPUZZLE_DESC|تخط اللغز الحالي.
MENU_ACCESSIBILITY_CAT_ASSISTS|خيارات المساعدة
MENU_ACCESSIBILITY_CAT_ASSISTS_DESC|اضبط خيارات المساعدة في القتال والحركة.
MENU_ACCESSIBILITY_CAT_GAMEPLAYANDCAMERA_DESC|اضبط إعدادات اللعب والكاميرا.
MENU_ACCESSIBILITY_CAT_PRESETS_DESC|اختر إعدادات جاهزة تضبط عدة خيارات لإمكانية الوصول معًا.
MENU_ACCESSIBILITY_CAT_VISUAL_DESC|اضبط إعدادات دوار الحركة والتباين وتمييز العناصر وواجهة المعلومات.
MENU_ACCESSIBILITY_DESC|اضبط خيارات إضافية لتسهيل الرؤية والإدراك والتحكم.
MENU_ACCESSIBILITY_DESC_FRONTEND|خيارات إضافية لتسهيل الرؤية والإدراك والتحكم.
MENU_ACCESSIBILITY_OPTION_HOLD|ضغط مستمر
MENU_ACCESSIBILITY_OPTION_TOGGLE|تبديل
MENU_ADAPTIVETRIGGERS_TITLE|الزنادات التكيفية
MENU_ADAPTIVETRIGGERS_OPTION_EXPERIENTIAL|غامر
MENU_ADAPTIVETRIGGERS_OPTION_EXPERIENTIAL_DESC|اشعر بالاهتزاز والمقاومة في [BTN_LT_GP] و[BTN_RT_GP] بما يتناسب مع أحداث اللعبة.
MENU_ADAPTIVETRIGGERS_OPTION_FUNCTIONAL_DESC|يقلل مقاومة [BTN_LT_GP] و[BTN_RT_GP] ويعطل الاهتزاز في [BTN_LT_GP] و[BTN_RT_GP].
MENU_ADAPTIVETRIGGERS_OPTION_NONE_DESC|يعطل الاهتزاز والمقاومة في [BTN_LT_GP] و[BTN_RT_GP].
MENU_AIMARC_DESC|اختر لون قوس مسار الرمي والأسلحة.
MENU_AIMMODE_DESC|اختر بين الضغط المستمر للتصويب والضغط مرة للتفعيل وأخرى للإيقاف.
MENU_AIMRETICLE_DESC|اختر لون مؤشر التصويب.
MENU_AIMRETICLE_TITLE|لون مؤشر التصويب
MENU_AIMSENSITIVITY_DESC|اضبط سرعة حركة الكاميرا أثناء التصويب. تقل السرعة عند خفض الحساسية وتزداد عند رفعها.
MENU_AIM_INVERTX_DESC|يعكس اتجاه حركة كاميرا التصويب أفقيًا.
MENU_AIM_INVERTX_TITLE|عكس التصويب الأفقي
MENU_AIM_INVERTY_DESC|يعكس اتجاه حركة كاميرا التصويب رأسيًا.
MENU_AIM_INVERTY_TITLE|عكس التصويب الرأسي
MENU_ALLYSHADER_TITLE|تمييز الحلفاء
MENU_ALLYSHADER_DESC|يميز الحلفاء بلون موحد لتسهيل رؤيتهم.
MENU_AUDIOBALANCE_DESC|اضبط توازن الصوت بين اليمين واليسار. القيمة 0 لليسار، و10 لليمين، و5 للمنتصف.
MENU_AUDIO_DESC|اضبط إعدادات الصوت.
MENU_AUTOSWAP_TITLE|التبديل التلقائي للسلاح
MENU_AUTOSWAP_DESC|يبدل إلى السلاح التالي تلقائيًا عند نفاد ذخيرة السلاح الحالي.
MENU_AUTOLEDGERECOVERY_TITLE|الحماية من السقوط خارج الشاشة
MENU_AUTOLEDGERECOVERY_DESC|يمنع السقوط غير المقصود من الحواف الموجودة خارج مجال الرؤية.
MENU_AUTOLEDGERECOVERY_OPTION_ALWAYS|مفعل دائمًا
MENU_BOOSTMODE_DESC|اختر بين الضغط المستمر للتسريع والضغط مرة للتفعيل وأخرى للإيقاف.
MENU_BOSSSHADER_TITLE|تمييز الزعماء
MENU_BOSSSHADER_DESC|يميز الزعماء بلون موحد.
MENU_BRIGHTNESS_DESC|اضبط سطوع الصورة. القيمة 0 هي الأغمق، والقيمة 100 هي الأكثر سطوعًا.
MENU_CAMERAFOLLOW_DESC|يدير الكاميرا تلقائيًا لتبقى خلف الشخصية أثناء الحركة.
MENU_CAMSENSITIVITY_DESC|اضبط سرعة حركة الكاميرا. تقل السرعة عند خفض الحساسية وتزداد عند رفعها.
MENU_CAMSHAKE_DESC|يفعل اهتزاز الشاشة أثناء اللعب، أو يعطله.
MENU_CHROMATICABERRATION_DESC|يحاكي انحراف الألوان عند حواف الصورة لإضفاء مظهر سينمائي.
MENU_COLLECTSHADER_TITLE|تمييز المقتنيات
MENU_COLLECTSHADER_DESC|يميز المقتنيات بلون موحد لتسهيل رؤيتها، مثل الراريتانيوم وروبوتات التجسس والمسامير الذهبية.
MENU_COLOR_OPTION_MAGENTA|أرجواني
MENU_COMPLETIONTIME_TITLE|زمن إكمال القصة
MENU_COMPLETIONTIME_DESC|يعرض الزمن المستغرق لإكمال القصة الرئيسية.
MENU_CONTRASTOPTIONS_DESC|استخدم الإعدادات المسبقة أو خصص ألوان تمييز العناصر والتباين العالي لتسهيل رؤيتها.
MENU_CONTRAST_DESC|اضبط تباين الصورة. القيمة 0 هي الأدنى، والقيمة 10 هي الأعلى.
MENU_CONTROLLERLAYOUT_DESC|اعرض توزيع أزرار جهاز التحكم وخصص وظائفها.
MENU_CONTROLSPEAKER_TITLE|مكبر صوت جهاز التحكم
MENU_CONTROLSPEAKER_VOL_TITLE|مستوى صوت جهاز التحكم
MENU_CONTROLSPEAKER_VOL_DESC|اضبط مستوى الصوت الصادر من مكبر جهاز التحكم.
MENU_CONTROLSPEAKER_OPTION_NONE_DESC|يعطل مكبر صوت جهاز التحكم.
MENU_CONTROLS_DESC|اعرض توزيع أزرار جهاز التحكم وخصص وظائفها والاختصارات.
MENU_CONTROLS_DESC_ALT|اعرض توزيع أزرار جهاز التحكم وخصص الاختصارات.
MENU_CONTROLS_DESC_DAY1|اعرض توزيع أزرار جهاز التحكم وخصص وظائفها والاختصارات وإعدادات الكاميرا.
MENU_DELETESAVE_BODY|سيؤدي حذف ملف الحفظ هذا إلى فقدان كل التقدم المسجل فيه نهائيًا.
MENU_DEPTHOFFIELDENABLED_DESC|يموه العناصر الواقعة خارج نطاق تركيز الكاميرا. يزداد التمويه كلما ابتعد العنصر عن نقطة التركيز.
MENU_DIFFICULTY_DESC|اختر مستوى صعوبة اللعبة.
MENU_DIFFICULTY_OPTION_EASY_DESC|للمبتدئين ومن يفضلون التركيز على القصة.
MENU_DIFFICULTY_OPTION_HARDEST_DESC|لمن يريدون مواجهة أشرس الأعداء في جميع الأبعاد!
MENU_DIFFICULTY_OPTION_HARD_DESC|لمن يبحثون عن تحد أكبر، مع أعداء أقوى ومواجهات تتطلب استجابة أسرع.
MENU_DIFFICULTY_OPTION_NORMAL_DESC|تجربة متوازنة للاعبين ذوي الخبرة.
MENU_DIFFICULTY_OPTION_SUPEREASY_DESC|لمن يفضلون التركيز على القصة. لا تموت الشخصية أثناء القتال في هذا المستوى.
MENU_DISABLEFULLSCREENFX_DESC|يفعل مؤثرات الشاشة مثل وهج العدسة والتموج الحراري وقطرات المطر وتأثيرات الغاز، أو يعطلها.
MENU_DISABLETUTORIALS_TITLE|تعطيل الإرشادات التعليمية
MENU_DISABLETUTORIALS_DESC|يعطل جميع الإرشادات التعليمية.
MENU_EASYAIM_TITLE|التثبيت التلقائي على الهدف
MENU_EASYAIM_DESC|يثبت التصويب على الأهداف عند الدخول في وضع التصويب.
MENU_EMPHASISCOLOR_TITLE|لون النص المميز
MENU_ENEMYSHADER_BASIC_TITLE|تمييز الأعداء العاديين
MENU_ENEMYSHADER_BASIC_DESC|يميز الأعداء العاديين بلون موحد.
MENU_ENEMYSHADER_TITLE|تمييز الأعداء
MENU_ENEMYSHADER_DESC|يميز الأعداء بلون موحد لتسهيل رؤيتهم. يمكنك أيضًا اختيار لون مختلف لكل فئة.
MENU_ENGLISH_VO_TITLE|الأصوات الإنجليزية
MENU_FILMGRAIN_TITLE|التحبب السينمائي
MENU_FILMGRAIN_DESC|اضبط شدة التحبب السينمائي. القيمة 0 هي الأدنى، والقيمة 10 هي الأعلى.
MENU_FLIGHTSTICK_TITLE|عصا التحكم بالطيران
MENU_FLIGHTSTICK_DESC|اختر العصا اليسرى أو اليمنى للتحكم بالطيران.
MENU_FLIGHT_INVERTX_TITLE|عكس الطيران الأفقي
MENU_FLIGHT_INVERTX_DESC|يعكس اتجاه التحكم بالطيران أفقيًا.
MENU_FLIGHT_INVERTY_TITLE|عكس الطيران الرأسي
MENU_FLIGHT_INVERTY_DESC|يعكس اتجاه التحكم بالطيران رأسيًا.
MENU_GAMEPAD_DESC|خصص أزرار جهاز التحكم والاختصارات والكاميرا والاهتزاز والزنادات التكيفية.
MENU_GAME_DESC|اضبط إعدادات اللعب والكاميرا والقتال والحركة.
MENU_GAME_DESC_DAY1|اضبط إعدادات اللعب والقتال والحركة.
MENU_GRINDASSIST_DESC|يبطئ الوقت تلقائيًا عند الاقتراب من خطر أثناء الانزلاق على القضبان.
MENU_HAPTICS_DESC|اضبط اهتزاز جهاز التحكم والزنادات التكيفية.
MENU_HAZARDSHADER_TITLE|تمييز المخاطر
MENU_HAZARDSHADER_DESC|يميز مصادر الخطر بلون موحد لتسهيل رؤيتها، مثل الصناديق المتفجرة والعناصر التي تسبب الضرر.
MENU_HEROSHADER_TITLE|تمييز الشخصية
MENU_HEROSHADER_DESC|يميز الشخصية التي تتحكم بها بلون موحد لتسهيل رؤيتها.
MENU_SETTINGS_CAT_HUD|واجهة المعلومات
MENU_SETTINGS_CAT_HUDCOLORS|ألوان واجهة المعلومات
MENU_SETTINGS_CAT_SHORTCUTS_DESC|خصص اختصارات اللعب والإعدادات وسرعة اللعبة.
MENU_SETTINGS_VISUAL_DESC|اضبط إعدادات العرض والمؤثرات البصرية.
MENU_SFX_VOL_DESC|اضبط مستوى المؤثرات الصوتية أثناء اللعب.
MENU_SHADEROUTLINE_TITLE|حدود عالية التباين
MENU_SHADEROUTLINE_DESC|يضيف حدودًا بلون موحد حول الشخصيات والأعداء لتسهيل رؤيتهم.
MENU_SHORTCUT_OPTION_MELEECOMBO|سلسلة ضربات اشتباك
MENU_SHORTCUT_OPTION_MELEECOMBO_DESC|ينفذ ثلاث ضربات اشتباك متتالية.
MENU_SHORTCUT_OPTION_MELEESLAM|ضربة اشتباك هابطة
MENU_SHORTCUT_OPTION_MELEESLAM_DESC|يقفز ثم يندفع إلى الأسفل بسلاح الاشتباك.
MENU_SHORTCUT_OPTION_MELEETHROW|رمي سلاح الاشتباك
MENU_SHORTCUT_OPTION_MELEETHROW_DESC|يرمي سلاح الاشتباك.
MENU_SHORTCUT_WEAPON_QS|اختيار سريع للسلاح
MENU_SPEECH_VOL_TITLE|مستوى صوت الحوار
MENU_SPEECH_VOL_DESC|اضبط مستوى أصوات الشخصيات أثناء الحوار.
MENU_SPEEDRUNNING_TITLE|الإنهاء السريع
MENU_SPEEDRUNNING_HEADER|إعدادات الإنهاء السريع
MENU_SPEEDRUNNING_DESC|اضبط الخيارات المساعدة على إنهاء اللعبة في أقصر وقت.
MENU_SUBS_TITLE|الترجمة
MENU_SUBS_DESC|يعرض ترجمة مكتوبة للحوار المنطوق.
MENU_SUBTITLES_TITLE|الترجمة
MENU_SUBTITLES_HEADER|إعدادات الترجمة
MENU_SUBTITLES_DESC|فعل الترجمة وخصص إعداداتها.
MENU_SUBTITLES_DESC_FRONTEND|خيارات تفعيل الترجمة وتخصيص مظهرها.
MENU_SUB_BG_TITLE|لون خلفية الترجمة
MENU_SUB_BG_DESC|يضيف خلفية متباينة خلف الترجمة لتسهيل قراءتها.
MENU_SUB_BG_OPACITY_TITLE|عتامة خلفية الترجمة
MENU_SUB_BG_OPACITY_DESC|اضبط عتامة خلفية الترجمة. القيمة 0 تخفي الخلفية.
MENU_SUB_COLOR_TITLE|لون الترجمة
MENU_SUB_COLOR_DESC|اختر لون نص الترجمة.
MENU_SUB_SIZE_TITLE|حجم الترجمة
MENU_SUB_SIZE_DESC|اضبط حجم نص الترجمة.
MENU_SUB_SPEAKER_COLOR_TITLE|لون اسم المتحدث
MENU_SUB_SPEAKER_COLOR_DESC|اختر لون اسم الشخصية المتحدثة في الترجمة.
MENU_SWINGAUTODETACH_TITLE|الإفلات التلقائي عند التأرجح
MENU_SWINGAUTODETACH_DESC|يفلت نقطة التعلق تلقائيًا عند الوصول إلى نهاية التأرجح.
MENU_TARGETRETICLE_TITLE|لون مؤشر الهدف
MENU_TARGETRETICLE_DESC|اختر لون مؤشر التصويب عند تمييز الهدف.
MENU_TIMEPLAYED_TITLE|عرض مدة اللعب
MENU_TIMEPLAYED_DESC|يعرض مؤقتًا يوضح الوقت المنقضي أثناء اللعب.
MENU_UI_VOL_DESC|اضبط مستوى المؤثرات الصوتية أثناء تصفح القوائم.
MENU_VIBRATION_INTENSITY_DESC|اضبط شدة اهتزاز جهاز التحكم.
MENU_VIBRATION_OPTION_EXPERIENTIAL_TITLE|غامر
MENU_VIBRATION_OPTION_EXPERIENTIAL_DESC|يفعل جميع الاهتزازات، بما فيها التفاصيل الدقيقة في البيئة والحركة.
MENU_VIBRATION_OPTION_FUNCTIONAL_DESC|يفعل الاهتزازات التي تنبهك إلى أحداث اللعب المهمة، مثل تلقي الضرر وجمع الصحة والذخيرة.
MENU_VIBRATION_OPTION_NONE_DESC|يعطل اهتزاز جهاز التحكم.
MENU_WAYPOINTS_SHOWALWAYS_TITLE|ظاهرة دائمًا
MENU_WEAPONLEVELPOPUPS_TITLE|تنبيهات ارتقاء الأسلحة
MENU_WEAPONLEVELPOPUPS_DESC|يعرض معلومات السلاح عند ارتفاع مستواه.
MENU_WEAPONWHEELPAUSE_TITLE|إيقاف اللعب عند فتح عجلة الأسلحة
MENU_WEAPONWHEELPAUSE_DESC|يوقف اللعب مؤقتًا أثناء فتح عجلة الأسلحة عند تفعيله. عند تعطيله، يستمر اللعب أثناء اختيار السلاح.
'''
changes={}
for line in DATA.strip().splitlines():
 k,v=line.split('|',1);assert k not in changes,k;changes[k]=v
# Wrap only editorial descriptions; renderer converts each line separately later.
for k in list(changes):
 if any(x in k for x in ('_DESC','_BODY','_HEADER')):
  words=re.findall(r'\[[^]]+\]|\S+',changes[k]);lines=[];line=[];width=0
  for w in words:
   if width+len(w)+bool(line)>32 and line:lines.append(' '.join(line));line=[];width=0
   line.append(w);width+=len(w)+bool(width)
  if line:lines.append(' '.join(line))
  changes[k]='<br>'.join(lines)
# Apply matching uppercase labels, used by the in-game UI.
allrows={}
for p in (R/'editable').rglob('*.json'):
 for row in json.loads(p.read_text()):allrows[row['key']]=row
for k,v in list(changes.items()):
 if k+'_UPPERCASE' in allrows:changes[k+'_UPPERCASE']=v
assert not (set(changes)-set(allrows)),set(changes)-set(allrows)
backup=R/'backups/editorial_before_settings';backup.mkdir(parents=True,exist_ok=True)
count=0
for p in (R/'editable').rglob('*.json'):
 rows=json.loads(p.read_text());dirty=False
 for r in rows:
  if r['key'] not in changes:continue
  if r['arabic_edit'] and r['arabic_edit']!=changes[r['key']]:raise RuntimeError('Existing edit: '+r['key'])
  r.update(arabic_edit=changes[r['key']],status='reviewed',notes='مراجعة لغوية للإعدادات، الدفعة 1. يحتاج العرض إلى اختبار داخل اللعبة.');count+=1;dirty=True
 if dirty:
  q=backup/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True)
  if not q.exists():q.write_bytes(p.read_bytes())
  p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(R/'patches/settings_editorial_batch1.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print('Editorial changes:',count)
