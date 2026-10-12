# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
import json,re
from text_layout import wrap_text
R=Path(__file__).resolve().parents[1]
D={
'CLANK_ANIMATICS_DRNEF1_002':['وهو يعرف وجهتنا.','يا إلهي.'],
'CLANK_ANIMATICS_DRNEF2_001':['يبدو أن الدكتور نيفاريوس سيفعل أي شيء للقبض علينا.'],
'DRNF_ANIMATICS_DRNEF1_001':['مرحبًا يا أهل هذا البعد!','أعلم أنني غبت مدة... تعرفون كم طالت،','لذا قلت لنلحق بما فاتنا!','ماذا كنت أفعل؟'],
'DRNF_ANIMATICS_DRNEF1_002':['أتحدث مع معجبي الأوفياء، لا أكثر...'],
'DRNF_ANIMATICS_DRNEF1_003':['وأستمتع بمناظري الخلابة...'],
'DRNF_ANIMATICS_DRNEF1_004':['وأكتشف وجود اثنين، *اثنين* من اللومباكس الوقحين،','يجوبان المكان ويحاولان إفساد كل شيء!'],
'DRNF_ANIMATICS_DRNEF1_005':['لذا! أعرض مكافأة قدرها ثلاثة سكويليون من قسائم الحرية النيفاريوسية،','لمن يحضر لي هذين المجرمين ذوي الفراء،','حيين أو ميتين!','ويفضل حيين، لأتسلى بهما أولًا!'],
'DRNF_ANIMATICS_DRNEF1_006':['تؤكد شبكة جواسيسي الواسعة أنهما سيصلان إلى بليزار وسافالي قريبًا. تحركوا!','وإن كان هذان اللومباكس يسمعانني، فليعلما أنني سأحولهما إلى غبار،','ثم أقذف الغبار في شمس، ثم ألقي تلك الشمس في...'],
'RIVE_ANIMATICS_DRNEF1_002':['رائع. أصبحت الآن على قائمتي اغتيال لنيفاريوس.'],
'DRNF_ANIMATICS_DRNEF2_001':['أتسمعون هذا؟!','هذا صوتي وأنا أسحق الأكاذيب!','أكاذيب قذرة ودنيئة!'],
'DRNF_ANIMATICS_DRNEF2_002':['يقولون: «هذا البعد غير مستقر، وسننجذب إلى فراغ بلا شكل».','كذب!','ومن يعتقد خلاف ذلك،','آمره أن يرمي عينيه في أقرب محرقة، فمن الواضح أنهما معطوبتان!'],
'DRNF_ANIMATICS_DRNEF2_003':['والأهم،','أن اللومباكس المخربين لم «يهربا».','وكيف يهربان وأنا لم أقبض عليهما أصلًا؟!','أيها الحمقى!'],
'DRNF_ANIMATICS_DRNEF2_004':['هاكم!','أتريدون الحقيقة؟!','صارت مكافأتي على اللومباكس 27 سكويجيليون نيفارباك!','انظروا إليها! ضخمة! حقيقية! وليست مختلقة أبدًا!','وستصبح كلها لكم حين تقبضون على هذين اللومباكس الغبيين!'],
'KIT_ANIMATICS_DRNEF2_001':['يبدو أن نيفاريوس عندكم بفظاعة نيفاريوس عندنا.'],
'RATC_ANIMATICS_DRNEF2_001':['أجل، إنه...','حالة فريدة فعلًا.'],
'RIVE_ANIMATICS_DRNEF2_001':['علينا أن نواصل السير.'],
'CLANK_ANOMALY_BLIZ_GP_003':['يبدو أن احتمالاتي تبقي ذلك الزر مضغوطًا!'],
'CLANK_ANOMALY_BLIZ_GP_011':['حقًا؟ كيف حاله؟'],
'CLANK_ANOMALY_BLIZ_GP_013':['أكنت تنتظرني؟'],
'CLANK_ANOMALY_BLIZ_GP_015':['كيف حصلت على لقب النبي إذن؟'],
'CLANK_ANOMALY_BLIZ_GP_017':['بخير إلى حد ما.','اخترقت دماغي واطلعت على ذكرياتي.'],
'CLANK_ANOMALY_BLIZ_GP_020':['هذا مثير للاهتمام؛','راتشت وريفت نظيران من بعدين مختلفين، ومع ذلك يختلفان بصورة مدهشة.','لم يرتب راتشت من الروبوتات حين قابلني،','أما ريفت فترتاب منها.'],
'CLANK_ANOMALY_BLIZ_GP_021':['هممم...'],
'CLANK_ANOMALY_BLIZ_GP_022':['كلاهما... يسارع إلى التصرف. أما أنا، فأظل غارقًا في التفاصيل.'],
'CLANK_ANOMALY_BLIZ_GP_023':['ليس *دائمًا*،','لكن أتمنى ألا أقلق إلى هذا الحد.'],
'CLANK_ANOMALY_BLIZ_GP_024':['ماذا تقصد؟'],
'CLANK_ANOMALY_BLIZ_GP_026':['شكرًا لك!'],
'CLANK_ANOMALY_BLIZ_GP_027':['وما معنى ذلك؟'],
'CLANK_ANOMALY_BLIZ_GP_028':['ماذا يحتوي كتابك هذا إذن؟'],
'CLANK_ANOMALY_BLIZ_GP_029':['ومن يكون؟'],
'CLANK_ANOMALY_BLIZ_GP_030':['*هو* والدك؟','ماذا يفعل الآن؟'],
'CLANK_ANOMALY_BLIZ_GP_034':['لا تستطيع احتمالاتي العبور وسط هذه الرياح.','هل يمكنني زيادة وزنها بطريقة ما؟'],
'CLANK_ANOMALY_BLIZ_GP_035':['لعل ذلك الجهاز يغير مسار احتمالاتي.','لا بد من وسيلة لتشغيله.'],
'CLANK_ANOMALY_BLIZ_GP_036':['احتمالاتي تجسيد مرئي لمحاولة عقلي فهم طبيعة الأبعاد.'],
'CLANK_ANOMALY_BLIZ_GP_037':['كلما ساعدتها على إيجاد طريقها،','ازداد فهمي وتمكنت من إصلاح...','كل شيء.'],
'CLANK_ANOMALY_BLIZ_GP_038':['ذلك المنشار يسد الطريق.','ليتني أجد وسيلة لإنزاله...'],
'PROPH_ANOMALY_BLIZ_GP_004':['لكنني خرجت عن الموضوع. احتمالاتك تنتظر أن توجهها إلى الطرفية العامة.'],
'PROPH_ANOMALY_BLIZ_GP_009':['آه! أصلحت الشذوذ البعدي في بليزار!','أحسنت يا كلانك!'],
'PROPH_ANOMALY_BLIZ_GP_010':['آه، تلك كرة ثقيلة!','تزيد وزن كل شيء تلمسه...','وهذا يبدو بديهيًا حين أقوله بصوت عالٍ، ها!'],
'PROPH_ANOMALY_BLIZ_GP_011':['كلانك! رأيت راتشت للتو!','في سافالي!'],
'PROPH_ANOMALY_BLIZ_GP_012':['بخير! أنحف مما تخيلت، لكنه بطل بحق.'],
'PROPH_ANOMALY_BLIZ_GP_013':['كلانك! لقد وصلت! بدأت أقلق عليك.'],
'PROPH_ANOMALY_BLIZ_GP_014':['بضع دقائق فقط، لكن لا بأس!','استغللت الوقت في إحصاء مخاوفي.'],
'PROPH_ANOMALY_BLIZ_GP_015':['في الحقيقة، لم أختر هذا الاسم.','منحني إياه رهبان سافالي بعد أن ساعدتهم في فك رموز بعض أرشيفاتهم.'],
'PROPH_ANOMALY_BLIZ_GP_017':['يا إلهي...','علي أن أدون هذا! كان ذلك مذهلًا يا كلانك! لم يبق إلا اثنان!'],
'PROPH_ANOMALY_BLIZ_GP_018':['كيف تسير الأمور مع ريفت؟'],
'PROPH_ANOMALY_BLIZ_GP_019':['أهذا ما تفعله الأجيال الجديدة هذه الأيام؟','يبدو أنني لا أواكب العصر.'],
'PROPH_ANOMALY_BLIZ_GP_021':['ربما بعدك هو الاستثناء؟','لعل نظراء راتشت في بقية الأبعاد لا يحبون الروبوتات أيضًا.'],
'PROPH_ANOMALY_BLIZ_GP_022':['رائع! لم أفكر في استخدام الكرة بهذه الطريقة...'],
'PROPH_ANOMALY_BLIZ_GP_023':['هل يشترك راتشت وريفت في أي شيء؟'],
'PROPH_ANOMALY_BLIZ_GP_024':['وتتمنى لو كنت أفضل في ذلك؟'],
'PROPH_ANOMALY_BLIZ_GP_025':['آه يا كلانك! أظنني عرفت حل مشكلتك مع الغرق في التفاصيل!','عليك فقط أن تثق بنفسك!'],
'PROPH_ANOMALY_BLIZ_GP_026':['إن تعلمت شيئًا من أبي،','فهو أن التصرف بثقة وكأنك تعرف ما تفعل يفتح لك أبواب الحياة.','هذا، وحمل مكبس تسليك.'],
'PROPH_ANOMALY_BLIZ_GP_028':['بل الشكر لك!','وتذكر: الثقة هي المفتاح!'],
'PROPH_ANOMALY_BLIZ_GP_029':['أوه، يشير إلى الأشياء ويقول مثلًا:','«هذا دليل هاتف بلارغي، وذلك سن كيرتشو، وهذه قصيدة حب تيراكلونية...»'],
'PROPH_ANOMALY_BLIZ_GP_030':['أحدث مجموعة معارف في الكون...','بحسب ما جمعه أبي ووثقه.'],
'PROPH_ANOMALY_BLIZ_GP_031':['أظنك تعرفه باسم السباك؟'],
'PROPH_ANOMALY_BLIZ_GP_032':['يقضي أول إجازة له...','في حياته. لذا ترك المسؤولية لي،','وأنا أبذل قصارى جهدي،','لكن الارتقاء إلى مستواه صعب، حتى حين لا يكون الكون في خطر.'],
}
T={
'PCDISPLAYSETTINGS_DLSS':'NVIDIA DLSS','PCDISPLAYSETTINGS_DLSSG':'DLSS Frame Generation',
'PCDISPLAYSETTINGS_FSRFRAMEGEN':'AMD FSR 3 Frame Generation','PCDISPLAYSETTINGS_VSYNC':'VSync',
'PCGRAPHICSSETTINGS_RAYTRACING':'Ray Tracing','PCGRAPHICSSETTINGS_RT_AMBIENTOCCLUSION':'Ray-Traced Ambient Occlusion',
'PCGRAPHICSSETTINGS_RT_REFLECTIONS':'Ray-Traced Reflections','PCGRAPHICSSETTINGS_RT_SHADOWS':'Ray-Traced Shadows',
'PCDISPLAYSETTINGS_UPSCALEMETHOD_DESC':'اختر تقنية تنعيم الحواف ورفع الدقة: Temporal Injection أو NVIDIA DLSS أو AMD FSR 3 أو Intel XeSS. اضبط الجودة ومعدل الإطارات المستهدف من الخيارات أدناه.',
'PCDISPLAYSETTINGS_NVIDIAREFLEX_DESC':'تقلل NVIDIA Reflex تأخير النظام وتحسن الاستجابة بتقليل تأخير GPU. يحاول وضع Boost تقليل تأخير CPU أيضًا.',
'PCDISPLAYSETTINGS_DLSSG_DESC':'تستخدم DLSS Frame Generation الذكاء الاصطناعي لتوليد إطارات إضافية مع الحفاظ على جودة الصورة والاستجابة. تتطلب بطاقة GeForce RTX 40 متوافقة.',
'PCDISPLAYSETTINGS_FRAMEGEN_DESC':'يولد Frame Generation إطارات إضافية اعتمادًا على بيانات الإطارات السابقة. تتطلب DLSS Frame Generation بطاقة GeForce RTX 40 متوافقة.',
'MENU_HDR_DESC':'تحسن HDR التباين ونطاق الألوان. لتفعيلها، افتح إعدادات النظام ثم الشاشة والفيديو ثم مخرج الفيديو ثم HDR. تتوفر على الشاشات المتوافقة فقط.',
'MENU_GRAPHICS_OPTION_FIDELITY_DESC':'وضع بمعدل 30 FPS ودقة 4K، مع Ray Tracing وإضاءة محسنة ومؤثرات بصرية إضافية وكثافة أكبر للمشهد. هذا هو الوضع الافتراضي.',
'MENU_GRAPHICS_OPTION_FIDELITY_DESC_DAY0':'وضع بمعدل 30 FPS، مع Ray Tracing وإضاءة محسنة ومؤثرات إضافية. تمنح التقنيات الزمنية صورة فائقة الجودة انطلاقًا من دقة 4K. هذا هو الوضع الافتراضي.<br><br>يتوفر وضع الأداء بمعدل 60 FPS في تحديث اليوم الأول.',
'MENU_GRAPHICS_OPTION_PERFORMANCE_DESC':'نسخة بديلة من وضع Performance RT بمعدل 60 FPS. تعطل Ray Tracing لتقديم صورة بدقة أعلى.',
'MENU_GRAPHICS_OPTION_PERFORMANCE_120_DESC':'نسخة بديلة من وضع Performance RT بمعدل 60 FPS. تعطل Ray Tracing لرفع دقة الصورة. عند تفعيل خرج 120 Hz في النظام، تصبح تقلبات معدل الإطارات أثناء اللعب المكثف أقل وضوحًا.',
'MENU_GRAPHICS_OPTION_PERFORMANCE_ONLY_DESC':'وضع بمعدل 60 FPS ودقة أقل، دون Ray Tracing أو الإضاءة المحسنة أو المؤثرات الإضافية أو الكثافة الأكبر للمشهد.',
'MENU_GRAPHICS_OPTION_PERFORMANCE_ONLY_120_DESC':'وضع بمعدل 60 FPS ودقة أقل، دون Ray Tracing أو الإضاءة المحسنة أو المؤثرات الإضافية أو الكثافة الأكبر للمشهد. عند تفعيل خرج 120 Hz في النظام، تصبح تقلبات معدل الإطارات أقل وضوحًا.',
'MENU_GRAPHICS_OPTION_PERFORMANCE_RT_DESC':'وضع بمعدل 60 FPS مع Ray Tracing. يقدم صورة بدقة أقل، مع تعديل الإضاءة والمؤثرات البصرية وكثافة المشهد.',
'MENU_GRAPHICS_OPTION_PERFORMANCE_RT_120_DESC':'وضع بمعدل 60 FPS مع Ray Tracing ودقة أقل، مع تعديل الإضاءة والمؤثرات وكثافة المشهد. عند تفعيل خرج 120 Hz في النظام، تصبح تقلبات معدل الإطارات أثناء اللعب المكثف أقل وضوحًا.'
}
for k,v in list(T.items()):
 if not k.endswith('_DESC'):T[k+'_UPPERCASE']=v
patch=[]
for p in (R/'editable').rglob('*.json'):
 rows=json.loads(p.read_text());dirty=False
 for r in rows:
  k=r['key'];new=None
  if k in D:
   tags=re.findall(r'<ts[^>]*>',r['arabic_current']);assert len(tags)==len(D[k]),k
   new=''.join(t+wrap_text(v,42) for t,v in zip(tags,D[k]))
  if k in T:new=wrap_text(T[k],34)
  if new is None:continue
  patch.append({'key':k,'before':r['arabic_edit'],'after':new})
  r.update(arabic_edit=new,status='reviewed',review_scope=['prose_v2'],reading_needs_review=False,notes='مراجعة لغوية بمقارنة النص الإنجليزي؛ اختبار العرض داخل اللعبة معلق.')
  dirty=True
 if dirty:p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(R/'patches/prose_v2.json').write_text(json.dumps(patch,ensure_ascii=False,indent=2)+'\n')
print('Prose/technology reviewed:',len(patch))
