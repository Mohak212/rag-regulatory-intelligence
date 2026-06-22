const state = {
  domain: "all",
  provider: "ollama",
  language: "english",
  domains: [],
};

const languageOptions = {
  english:   { label: "English",    speech: "en-IN" },
  hindi:     { label: "हिन्दी",      speech: "hi-IN" },
  bengali:   { label: "বাংলা",       speech: "bn-IN" },
  gujarati:  { label: "ગુજરાતી",     speech: "gu-IN" },
  kannada:   { label: "ಕನ್ನಡ",       speech: "kn-IN" },
  malayalam: { label: "മലയാളം",      speech: "ml-IN" },
  marathi:   { label: "मराठी",       speech: "mr-IN" },
  odia:      { label: "ଓଡ଼ିଆ",       speech: "or-IN" },
  punjabi:   { label: "ਪੰਜਾਬੀ",      speech: "pa-IN" },
  tamil:     { label: "தமிழ்",       speech: "ta-IN" },
  telugu:    { label: "తెలుగు",      speech: "te-IN" },
};

const translations = {
  english: {
    app_eyebrow:      "RAG Regulatory Intelligence",
    app_title:        "Ask SEBI and RBI circulars",
    language_trigger: "Language",
    checking_index:   "Checking index",
    question_label:   "Question",
    voice_btn:        "🎙 Voice",
    voice_listening:  "🎙 Listening…",
    placeholder:      "Ask about P2P lending, credit rating agencies, debenture trustees, KYC, remittance limits…",
    domain_label:     "Domain",
    domain_all:       "All",
    domain_tax:       "Income Tax",
    provider_label:   "Answer Provider",
    sources_only:     "Sources",
    topk_label:       "Top K",
    lang_label:       "Answer Language",
    ollama_label:     "Ollama model",
    openai_label:     "OpenAI model",
    hf_label:         "Include Hugging Face RBI QA experimental data",
    ask_btn:          "Ask",
    ask_working:      "Working…",
    sample_btn:       "Use sample",
    empty_title:      "Ready for a source-backed answer",
    empty_body:       "Select a domain, ask a question, and the system will retrieve matching chunks before generating a cited response.",
    loading_title:    "Retrieving and drafting",
    loading_body:     "Local Ollama can take a minute or two. OpenAI will be faster once configured.",
    answer_eyebrow:   "Answer",
    answer_title:     "Generated response",
    sources_eyebrow:  "Sources",
    sources_title:    "Retrieved context",
    tax_note:         "Income Tax documents are not present in this corpus yet.",
    gate_eyebrow:     "Welcome",
    gate_title:       "Choose your preferred language",
    gate_copy:        "The app will answer in this language and use it for voice input. You can change it anytime.",
    error_empty:      "Type a question first.",
    error_voice:      "Voice input is not supported in this browser. Try Chrome or Edge.",
    no_sources:       "No sources returned.",
  },
  hindi: {
    app_eyebrow:      "RAG विनियामक बुद्धिमत्ता",
    app_title:        "SEBI और RBI परिपत्रों से पूछें",
    language_trigger: "भाषा",
    checking_index:   "सूचकांक जाँच रहा है",
    question_label:   "प्रश्न",
    voice_btn:        "🎙 आवाज़",
    voice_listening:  "🎙 सुन रहा है…",
    placeholder:      "P2P उधार, क्रेडिट रेटिंग एजेंसियों, डिबेंचर ट्रस्टी, KYC, प्रेषण सीमाओं के बारे में पूछें…",
    domain_label:     "क्षेत्र",
    domain_all:       "सभी",
    domain_tax:       "आयकर",
    provider_label:   "उत्तर प्रदाता",
    sources_only:     "स्रोत",
    topk_label:       "Top K",
    lang_label:       "उत्तर की भाषा",
    ollama_label:     "Ollama मॉडल",
    openai_label:     "OpenAI मॉडल",
    hf_label:         "Hugging Face RBI QA प्रायोगिक डेटा शामिल करें",
    ask_btn:          "पूछें",
    ask_working:      "काम हो रहा है…",
    sample_btn:       "नमूना उपयोग करें",
    empty_title:      "स्रोत-समर्थित उत्तर के लिए तैयार",
    empty_body:       "एक क्षेत्र चुनें, प्रश्न पूछें, और सिस्टम उद्धृत प्रतिक्रिया उत्पन्न करने से पहले मिलान अंश खोजेगा।",
    loading_title:    "खोज और मसौदा तैयार हो रहा है",
    loading_body:     "स्थानीय Ollama में एक-दो मिनट लग सकते हैं। OpenAI कॉन्फ़िगर होने पर तेज़ होगा।",
    answer_eyebrow:   "उत्तर",
    answer_title:     "उत्पन्न प्रतिक्रिया",
    sources_eyebrow:  "स्रोत",
    sources_title:    "पुनः प्राप्त संदर्भ",
    tax_note:         "आयकर दस्तावेज़ अभी इस संग्रह में उपलब्ध नहीं हैं।",
    gate_eyebrow:     "स्वागत है",
    gate_title:       "अपनी पसंदीदा भाषा चुनें",
    gate_copy:        "ऐप इस भाषा में उत्तर देगा और आवाज़ इनपुट के लिए इसका उपयोग करेगा। आप इसे कभी भी बदल सकते हैं।",
    error_empty:      "पहले एक प्रश्न टाइप करें।",
    error_voice:      "इस ब्राउज़र में आवाज़ इनपुट समर्थित नहीं है। Chrome या Edge आज़माएं।",
    no_sources:       "कोई स्रोत नहीं मिला।",
  },
  bengali: {
    app_eyebrow:      "RAG নিয়ন্ত্রক বুদ্ধিমত্তা",
    app_title:        "SEBI ও RBI সার্কুলার সম্পর্কে জিজ্ঞাসা করুন",
    language_trigger: "ভাষা",
    checking_index:   "সূচক যাচাই হচ্ছে",
    question_label:   "প্রশ্ন",
    voice_btn:        "🎙 ভয়েস",
    voice_listening:  "🎙 শুনছে…",
    placeholder:      "P2P ঋণ, ক্রেডিট রেটিং সংস্থা, ডিবেঞ্চার ট্রাস্টি, KYC, রেমিট্যান্স সীমা সম্পর্কে জিজ্ঞাসা করুন…",
    domain_label:     "ডোমেন",
    domain_all:       "সব",
    domain_tax:       "আয়কর",
    provider_label:   "উত্তর প্রদানকারী",
    sources_only:     "উৎস",
    topk_label:       "Top K",
    lang_label:       "উত্তরের ভাষা",
    ollama_label:     "Ollama মডেল",
    openai_label:     "OpenAI মডেল",
    hf_label:         "Hugging Face RBI QA পরীক্ষামূলক ডেটা অন্তর্ভুক্ত করুন",
    ask_btn:          "জিজ্ঞাসা করুন",
    ask_working:      "কাজ চলছে…",
    sample_btn:       "নমুনা ব্যবহার করুন",
    empty_title:      "উৎস-সমর্থিত উত্তরের জন্য প্রস্তুত",
    empty_body:       "একটি ডোমেন বেছে নিন, প্রশ্ন করুন, এবং সিস্টেম উদ্ধৃত উত্তর তৈরির আগে প্রাসঙ্গিক অংশ খুঁজবে।",
    loading_title:    "তথ্য সংগ্রহ ও খসড়া তৈরি হচ্ছে",
    loading_body:     "স্থানীয় Ollama এক-দুই মিনিট নিতে পারে। কনফিগার করা হলে OpenAI দ্রুত হবে।",
    answer_eyebrow:   "উত্তর",
    answer_title:     "উৎপন্ন প্রতিক্রিয়া",
    sources_eyebrow:  "উৎস",
    sources_title:    "পুনরুদ্ধৃত প্রসঙ্গ",
    tax_note:         "আয়কর দলিল এখনও এই সংগ্রহে নেই।",
    gate_eyebrow:     "স্বাগতম",
    gate_title:       "আপনার পছন্দের ভাষা বেছে নিন",
    gate_copy:        "অ্যাপটি এই ভাষায় উত্তর দেবে এবং ভয়েস ইনপুটের জন্য এটি ব্যবহার করবে। আপনি যেকোনো সময় পরিবর্তন করতে পারেন।",
    error_empty:      "আগে একটি প্রশ্ন টাইপ করুন।",
    error_voice:      "এই ব্রাউজারে ভয়েস ইনপুট সমর্থিত নয়। Chrome বা Edge ব্যবহার করুন।",
    no_sources:       "কোনো উৎস পাওয়া যায়নি।",
  },
  gujarati: {
    app_eyebrow:      "RAG નિયમનકારી બુદ્ધિমત્તા",
    app_title:        "SEBI અને RBI પરિપત્રો વિશે પૂછો",
    language_trigger: "ભાષા",
    checking_index:   "સૂચકાંક તપાસી રહ્યું છે",
    question_label:   "પ્રશ્ન",
    voice_btn:        "🎙 અવાજ",
    voice_listening:  "🎙 સાંભળી રહ્યું છે…",
    placeholder:      "P2P ધિરાણ, ક્રેડિટ રેટિંગ એજન્સીઓ, ડિબેન્ચર ટ્રસ્ટી, KYC, રેમિટન્સ મર્યાદા વિશે પૂછો…",
    domain_label:     "ક્ષેત્ર",
    domain_all:       "બધા",
    domain_tax:       "આવકવેરો",
    provider_label:   "ઉત્તર પ્રદાતા",
    sources_only:     "સ્ત્રોત",
    topk_label:       "Top K",
    lang_label:       "ઉત્તરની ભાષા",
    ollama_label:     "Ollama મૉડેલ",
    openai_label:     "OpenAI મૉડેલ",
    hf_label:         "Hugging Face RBI QA પ્રાયોગિક ડેટા સામેલ કરો",
    ask_btn:          "પૂછો",
    ask_working:      "કામ ચાલી રહ્યું છે…",
    sample_btn:       "નમૂનો વાપરો",
    empty_title:      "સ્ત્રોત-સમર્થિત ઉત્તર માટે તૈયાર",
    empty_body:       "ક્ષેત્ર પસંદ કરો, પ્રશ્ન પૂછો, અને સિસ્ટમ ઉદ્ધૃત પ્રતિભાવ પહેલા મેળ ખાતા ટુકડા શોધશે।",
    loading_title:    "ડેટા મેળવી રહ્યું છે અને ડ્રાફ્ટ કરી રહ્યું છે",
    loading_body:     "સ્થાનિક Ollama એક-બે મિનિટ લઈ શકે. OpenAI ગોઠવ્યા પછી ઝડપી હશે.",
    answer_eyebrow:   "ઉત્તર",
    answer_title:     "ઉત્પન્ન પ્રતિભાવ",
    sources_eyebrow:  "સ્ત્રોત",
    sources_title:    "પ્રાપ્ત સંદર્ભ",
    tax_note:         "આ સંગ્રહમાં આવકવેરા દસ્તાવેજો હજી ઉપલબ્ધ નથી.",
    gate_eyebrow:     "સ્વાગત",
    gate_title:       "તમારી પ્રિય ભાષા પસંદ કરો",
    gate_copy:        "એપ આ ભાષામાં ઉત્તર આપશે અને વૉઇસ ઇનપુટ માટે તેનો ઉપયોગ કરશે. તમે ગમે ત્યારે બદલી શકો છો.",
    error_empty:      "પ્રથમ એક પ્રશ્ન ટાઇપ કરો.",
    error_voice:      "આ બ્રાઉઝરમાં વૉઇસ ઇનપુટ સપોર્ટ નથી. Chrome અથવા Edge અજમાવો.",
    no_sources:       "કોઈ સ્ત્રોત મળ્યો નથી.",
  },
  kannada: {
    app_eyebrow:      "RAG ನಿಯಂತ್ರಕ ಬುದ್ಧಿಮತ್ತೆ",
    app_title:        "SEBI ಮತ್ತು RBI ಸುತ್ತೋಲೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ",
    language_trigger: "ಭಾಷೆ",
    checking_index:   "ಸೂಚ್ಯಂಕ ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ",
    question_label:   "ಪ್ರಶ್ನೆ",
    voice_btn:        "🎙 ಧ್ವನಿ",
    voice_listening:  "🎙 ಆಲಿಸುತ್ತಿದೆ…",
    placeholder:      "P2P ಸಾಲ, ಕ್ರೆಡಿಟ್ ರೇಟಿಂಗ್ ಏಜೆನ್ಸಿಗಳು, ಡಿಬೆಂಚರ್ ಟ್ರಸ್ಟಿ, KYC, ರೆಮಿಟೆನ್ಸ್ ಮಿತಿಗಳ ಬಗ್ಗೆ ಕೇಳಿ…",
    domain_label:     "ಡೊಮೈನ್",
    domain_all:       "ಎಲ್ಲಾ",
    domain_tax:       "ಆದಾಯ ತೆರಿಗೆ",
    provider_label:   "ಉತ್ತರ ಪೂರೈಕೆದಾರ",
    sources_only:     "ಮೂಲಗಳು",
    topk_label:       "Top K",
    lang_label:       "ಉತ್ತರದ ಭಾಷೆ",
    ollama_label:     "Ollama ಮಾಡೆಲ್",
    openai_label:     "OpenAI ಮಾಡೆಲ್",
    hf_label:         "Hugging Face RBI QA ಪ್ರಾಯೋಗಿಕ ಡೇಟಾ ಸೇರಿಸಿ",
    ask_btn:          "ಕೇಳಿ",
    ask_working:      "ಕಾರ್ಯ ನಡೆಯುತ್ತಿದೆ…",
    sample_btn:       "ಮಾದರಿ ಬಳಸಿ",
    empty_title:      "ಮೂಲ-ಆಧಾರಿತ ಉತ್ತರಕ್ಕೆ ಸಿದ್ಧ",
    empty_body:       "ಡೊಮೈನ್ ಆಯ್ಕೆ ಮಾಡಿ, ಪ್ರಶ್ನೆ ಕೇಳಿ, ಸಿಸ್ಟಂ ಉದ್ಧೃತ ಪ್ರತಿಕ್ರಿಯೆ ನೀಡುವ ಮೊದಲು ಹೊಂದಾಣಿಕೆ ತುಣುಕುಗಳನ್ನು ಹುಡುಕುತ್ತದೆ.",
    loading_title:    "ಮಾಹಿತಿ ಸಂಗ್ರಹಿಸಲಾಗುತ್ತಿದೆ",
    loading_body:     "ಸ್ಥಳೀಯ Ollama ಒಂದೆರಡು ನಿಮಿಷ ತೆಗೆದುಕೊಳ್ಳಬಹುದು. OpenAI ಹೊಂದಿಸಿದ ನಂತರ ವೇಗವಾಗಿರುತ್ತದೆ.",
    answer_eyebrow:   "ಉತ್ತರ",
    answer_title:     "ಉತ್ಪಾದಿತ ಪ್ರತಿಕ್ರಿಯೆ",
    sources_eyebrow:  "ಮೂಲಗಳು",
    sources_title:    "ಹಿಂಪಡೆದ ಸಂದರ್ಭ",
    tax_note:         "ಆದಾಯ ತೆರಿಗೆ ದಾಖಲೆಗಳು ಇನ್ನೂ ಈ ಕಾರ್ಪಸ್‌ನಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲ.",
    gate_eyebrow:     "ಸ್ವಾಗತ",
    gate_title:       "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆ ಆಯ್ಕೆ ಮಾಡಿ",
    gate_copy:        "ಆ್ಯಪ್ ಈ ಭಾಷೆಯಲ್ಲಿ ಉತ್ತರಿಸುತ್ತದೆ ಮತ್ತು ಧ್ವನಿ ಇನ್‌ಪುಟ್‌ಗಾಗಿ ಇದನ್ನು ಬಳಸುತ್ತದೆ. ನೀವು ಯಾವಾಗ ಬೇಕಾದರೂ ಬದಲಾಯಿಸಬಹುದು.",
    error_empty:      "ಮೊದಲು ಒಂದು ಪ್ರಶ್ನೆ ಟೈಪ್ ಮಾಡಿ.",
    error_voice:      "ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಇನ್‌ಪುಟ್ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. Chrome ಅಥವಾ Edge ಪ್ರಯತ್ನಿಸಿ.",
    no_sources:       "ಯಾವುದೇ ಮೂಲಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
  },
  malayalam: {
    app_eyebrow:      "RAG റെഗുലേറ്ററി ഇന്റലിജൻസ്",
    app_title:        "SEBI, RBI സർക്കുലറുകളെ കുറിച്ച് ചോദിക്കുക",
    language_trigger: "ഭാഷ",
    checking_index:   "സൂചിക പരിശോധിക്കുന്നു",
    question_label:   "ചോദ്യം",
    voice_btn:        "🎙 ശബ്ദം",
    voice_listening:  "🎙 കേൾക്കുന്നു…",
    placeholder:      "P2P വായ്‌പ, ക്രെഡിറ്റ് റേറ്റിംഗ് ഏജൻസികൾ, ഡിബഞ്ചർ ട്രസ്റ്റി, KYC, റെമിറ്റൻസ് പരിധി എന്നിവ കുറിച്ച് ചോദിക്കുക…",
    domain_label:     "ഡൊമൈൻ",
    domain_all:       "എല്ലാം",
    domain_tax:       "ആദായ നികുതി",
    provider_label:   "ഉത്തര ദാതാവ്",
    sources_only:     "ഉറവിടങ്ങൾ",
    topk_label:       "Top K",
    lang_label:       "ഉത്തരത്തിന്റെ ഭാഷ",
    ollama_label:     "Ollama മോഡൽ",
    openai_label:     "OpenAI മോഡൽ",
    hf_label:         "Hugging Face RBI QA പരീക്ഷണ ഡേറ്റ ഉൾപ്പെടുത്തുക",
    ask_btn:          "ചോദിക്കുക",
    ask_working:      "പ്രവർത്തിക്കുന്നു…",
    sample_btn:       "സാമ്പിൾ ഉപയോഗിക്കുക",
    empty_title:      "ഉറവിട-പിന്തുണയുള്ള ഉത്തരത്തിന് തയ്യാർ",
    empty_body:       "ഒരു ഡൊമൈൻ തിരഞ്ഞെടുക്കുക, ചോദ്യം ചോദിക്കുക, സിസ്റ്റം ഉദ്ധൃത പ്രതികരണം നൽകുന്നതിന് മുൻപ് ഉചിതമായ ഭാഗങ്ങൾ കണ്ടെത്തും.",
    loading_title:    "ഡേറ്റ ശേഖരിക്കുകയും ഡ്രാഫ്റ്റ് ചെയ്യുകയും ചെയ്യുന്നു",
    loading_body:     "ലോക്കൽ Ollama ഒന്നോ രണ്ടോ മിനിറ്റ് എടുക്കാം. OpenAI ക്രമീകരിച്ചാൽ വേഗത്തിലാകും.",
    answer_eyebrow:   "ഉത്തരം",
    answer_title:     "ജനറേറ്റ് ചെയ്ത പ്രതികരണം",
    sources_eyebrow:  "ഉറവിടങ്ങൾ",
    sources_title:    "വീണ്ടെടുത്ത സന്ദർഭം",
    tax_note:         "ആദായ നികുതി രേഖകൾ ഇതുവരെ ഈ ശേഖരത്തിൽ ഇല്ല.",
    gate_eyebrow:     "സ്വാഗതം",
    gate_title:       "നിങ്ങളുടെ ഇഷ്ടഭാഷ തിരഞ്ഞെടുക്കുക",
    gate_copy:        "ആപ്പ് ഈ ഭാഷയിൽ ഉത്തരം നൽകുകയും ശബ്ദ ഇൻപുട്ടിനായി ഉപയോഗിക്കുകയും ചെയ്യും. ഏത് സമയത്തും മാറ്റാവുന്നതാണ്.",
    error_empty:      "ആദ്യം ഒരു ചോദ്യം ടൈപ്പ് ചെയ്യുക.",
    error_voice:      "ഈ ബ്രൗസറിൽ ശബ്ദ ഇൻപുട്ട് പിന്തുണയ്ക്കില്ല. Chrome അല്ലെങ്കിൽ Edge പരീക്ഷിക്കുക.",
    no_sources:       "ഉറവിടങ്ങളൊന്നും കണ്ടെത്തിയില്ല.",
  },
  marathi: {
    app_eyebrow:      "RAG नियामक बुद्धिमत्ता",
    app_title:        "SEBI आणि RBI परिपत्रकांबद्दल विचारा",
    language_trigger: "भाषा",
    checking_index:   "निर्देशांक तपासत आहे",
    question_label:   "प्रश्न",
    voice_btn:        "🎙 आवाज",
    voice_listening:  "🎙 ऐकत आहे…",
    placeholder:      "P2P कर्ज, क्रेडिट रेटिंग एजन्सी, डिबेंचर ट्रस्टी, KYC, प्रेषण मर्यादांबद्दल विचारा…",
    domain_label:     "क्षेत्र",
    domain_all:       "सर्व",
    domain_tax:       "आयकर",
    provider_label:   "उत्तर प्रदाता",
    sources_only:     "स्रोत",
    topk_label:       "Top K",
    lang_label:       "उत्तराची भाषा",
    ollama_label:     "Ollama मॉडेल",
    openai_label:     "OpenAI मॉडेल",
    hf_label:         "Hugging Face RBI QA प्रायोगिक डेटा समाविष्ट करा",
    ask_btn:          "विचारा",
    ask_working:      "काम सुरू आहे…",
    sample_btn:       "नमुना वापरा",
    empty_title:      "स्रोत-समर्थित उत्तरासाठी तयार",
    empty_body:       "एक क्षेत्र निवडा, प्रश्न विचारा, सिस्टम उद्धृत प्रतिसाद देण्यापूर्वी जुळणारे तुकडे शोधेल.",
    loading_title:    "माहिती मिळवत आहे आणि मसुदा तयार करत आहे",
    loading_body:     "स्थानिक Ollama एक-दोन मिनिटे घेऊ शकतो. OpenAI कॉन्फिगर केल्यावर जलद होईल.",
    answer_eyebrow:   "उत्तर",
    answer_title:     "उत्पन्न प्रतिसाद",
    sources_eyebrow:  "स्रोत",
    sources_title:    "पुनर्प्राप्त संदर्भ",
    tax_note:         "आयकर दस्तऐवज अद्याप या संग्रहात उपलब्ध नाहीत.",
    gate_eyebrow:     "स्वागत",
    gate_title:       "तुमची आवडती भाषा निवडा",
    gate_copy:        "अॅप या भाषेत उत्तर देईल आणि आवाज इनपुटसाठी वापरेल. तुम्ही कधीही बदलू शकता.",
    error_empty:      "आधी एक प्रश्न टाइप करा.",
    error_voice:      "या ब्राउझरमध्ये आवाज इनपुट समर्थित नाही. Chrome किंवा Edge वापरून पहा.",
    no_sources:       "कोणतेही स्रोत मिळाले नाहीत.",
  },
  odia: {
    app_eyebrow:      "RAG ନିୟାମକ ବୁଦ୍ଧିମତ୍ତା",
    app_title:        "SEBI ଓ RBI ସର୍କୁଲାର ସମ୍ପର୍କରେ ପ୍ରଶ୍ନ କରନ୍ତୁ",
    language_trigger: "ଭାଷା",
    checking_index:   "ସୂଚୀ ଯାଞ୍ଚ ହେଉଛି",
    question_label:   "ପ୍ରଶ୍ନ",
    voice_btn:        "🎙 ଧ୍ୱନି",
    voice_listening:  "🎙 ଶୁଣୁଛି…",
    placeholder:      "P2P ଋଣ, ଋଣ ମୂଲ୍ୟାଙ୍କନ ସଂସ୍ଥା, ଡିବେଞ୍ଚର ଟ୍ରଷ୍ଟି, KYC, ଅନୁପ୍ରେଷଣ ସୀମା ବିଷୟରେ ପ୍ରଶ୍ନ କରନ୍ତୁ…",
    domain_label:     "ଡୋମେନ",
    domain_all:       "ସମସ୍ତ",
    domain_tax:       "ଆୟକର",
    provider_label:   "ଉତ୍ତର ପ୍ରଦାନକାରୀ",
    sources_only:     "ଉତ୍ସ",
    topk_label:       "Top K",
    lang_label:       "ଉତ୍ତରର ଭାଷା",
    ollama_label:     "Ollama ମଡେଲ",
    openai_label:     "OpenAI ମଡେଲ",
    hf_label:         "Hugging Face RBI QA ପ୍ରାୟୋଗିକ ତଥ୍ୟ ଅନ୍ତର୍ଭୁକ୍ତ କରନ୍ତୁ",
    ask_btn:          "ପ୍ରଶ୍ନ କରନ୍ତୁ",
    ask_working:      "କାର୍ଯ୍ୟ ଚାଲୁ ଅଛି…",
    sample_btn:       "ନମୁନା ବ୍ୟବହାର କରନ୍ତୁ",
    empty_title:      "ଉତ୍ସ-ସମର୍ଥିତ ଉତ୍ତର ପାଇଁ ପ୍ରସ୍ତୁତ",
    empty_body:       "ଏକ ଡୋମେନ ବାଛନ୍ତୁ, ପ୍ରଶ୍ନ କରନ୍ତୁ, ସିଷ୍ଟମ ଉଦ୍ଧୃତ ଉତ୍ତର ଦେବା ପୂର୍ବରୁ ମେଳ ଖାଉଥିବା ଅଂଶ ଖୋଜିବ।",
    loading_title:    "ତଥ୍ୟ ସଂଗ୍ରହ ଓ ଖସଡ଼ା ପ୍ରସ୍ତୁତ ହେଉଛି",
    loading_body:     "ସ୍ଥାନୀୟ Ollama ଗୋଟିଏ-ଦୁଇ ମିନିଟ ଲାଗିପାରେ। OpenAI ସଂରଚନା ପରେ ଦ୍ରୁତ ହେବ।",
    answer_eyebrow:   "ଉତ୍ତର",
    answer_title:     "ଉତ୍ପନ୍ନ ପ୍ରତିକ୍ରିୟା",
    sources_eyebrow:  "ଉତ୍ସ",
    sources_title:    "ପୁନରୁଦ୍ଧାର ପ୍ରସଙ୍ଗ",
    tax_note:         "ଆୟକର ଦଲିଲ ଏହି ସଂଗ୍ରହରେ ଏପର୍ଯ୍ୟନ୍ତ ଉପଲବ୍ଧ ନୁହଁ।",
    gate_eyebrow:     "ସ୍ୱାଗତ",
    gate_title:       "ଆପଣଙ୍କ ପସନ୍ଦର ଭାଷା ବାଛନ୍ତୁ",
    gate_copy:        "ଆପ୍ ଏହି ଭାଷାରେ ଉତ୍ତର ଦେବ ଓ ଧ୍ୱନି ଇନପୁଟ ପାଇଁ ଏହା ବ୍ୟବହାର ହେବ। ଆପଣ ଯେକୌଣସି ସମୟରେ ବଦଳାଇ ପାରିବେ।",
    error_empty:      "ପ୍ରଥମେ ଏକ ପ୍ରଶ୍ନ ଟାଇପ୍ କରନ୍ତୁ।",
    error_voice:      "ଏହି ବ୍ରାଉଜରରେ ଧ୍ୱନି ଇନପୁଟ ସମର୍ଥିତ ନୁହଁ। Chrome ବା Edge ଚେଷ୍ଟା କରନ୍ତୁ।",
    no_sources:       "କୌଣସି ଉତ୍ସ ମିଳିଲା ନାହିଁ।",
  },
  punjabi: {
    app_eyebrow:      "RAG ਰੈਗੂਲੇਟਰੀ ਇੰਟੈਲੀਜੈਂਸ",
    app_title:        "SEBI ਅਤੇ RBI ਸਰਕੁਲਰਾਂ ਬਾਰੇ ਪੁੱਛੋ",
    language_trigger: "ਭਾਸ਼ਾ",
    checking_index:   "ਸੂਚਕਾਂਕ ਜਾਂਚਿਆ ਜਾ ਰਿਹਾ ਹੈ",
    question_label:   "ਸਵਾਲ",
    voice_btn:        "🎙 ਆਵਾਜ਼",
    voice_listening:  "🎙 ਸੁਣ ਰਿਹਾ ਹੈ…",
    placeholder:      "P2P ਕਰਜ਼ਾ, ਕ੍ਰੈਡਿਟ ਰੇਟਿੰਗ ਏਜੰਸੀਆਂ, ਡਿਬੈਂਚਰ ਟਰੱਸਟੀ, KYC, ਰੈਮਿਟੈਂਸ ਸੀਮਾਵਾਂ ਬਾਰੇ ਪੁੱਛੋ…",
    domain_label:     "ਡੋਮੇਨ",
    domain_all:       "ਸਾਰੇ",
    domain_tax:       "ਆਮਦਨ ਕਰ",
    provider_label:   "ਉੱਤਰ ਪ੍ਰਦਾਤਾ",
    sources_only:     "ਸਰੋਤ",
    topk_label:       "Top K",
    lang_label:       "ਉੱਤਰ ਦੀ ਭਾਸ਼ਾ",
    ollama_label:     "Ollama ਮਾਡਲ",
    openai_label:     "OpenAI ਮਾਡਲ",
    hf_label:         "Hugging Face RBI QA ਪ੍ਰਯੋਗਾਤਮਕ ਡੇਟਾ ਸ਼ਾਮਲ ਕਰੋ",
    ask_btn:          "ਪੁੱਛੋ",
    ask_working:      "ਕੰਮ ਚੱਲ ਰਿਹਾ ਹੈ…",
    sample_btn:       "ਨਮੂਨਾ ਵਰਤੋ",
    empty_title:      "ਸਰੋਤ-ਸਮਰਥਿਤ ਉੱਤਰ ਲਈ ਤਿਆਰ",
    empty_body:       "ਡੋਮੇਨ ਚੁਣੋ, ਸਵਾਲ ਪੁੱਛੋ, ਸਿਸਟਮ ਹਵਾਲੇ ਵਾਲਾ ਜਵਾਬ ਦੇਣ ਤੋਂ ਪਹਿਲਾਂ ਮੇਲ ਖਾਂਦੇ ਟੁਕੜੇ ਲੱਭੇਗਾ।",
    loading_title:    "ਡੇਟਾ ਲਿਆ ਜਾ ਰਿਹਾ ਹੈ ਅਤੇ ਡਰਾਫਟ ਤਿਆਰ ਹੋ ਰਿਹਾ ਹੈ",
    loading_body:     "ਸਥਾਨਕ Ollama ਇੱਕ-ਦੋ ਮਿੰਟ ਲੈ ਸਕਦਾ ਹੈ। OpenAI ਕੌਂਫਿਗਰ ਕਰਨ ਤੋਂ ਬਾਅਦ ਤੇਜ਼ ਹੋਵੇਗਾ।",
    answer_eyebrow:   "ਉੱਤਰ",
    answer_title:     "ਉਤਪੰਨ ਜਵਾਬ",
    sources_eyebrow:  "ਸਰੋਤ",
    sources_title:    "ਪ੍ਰਾਪਤ ਸੰਦਰਭ",
    tax_note:         "ਆਮਦਨ ਕਰ ਦਸਤਾਵੇਜ਼ ਅਜੇ ਇਸ ਸੰਗ੍ਰਹਿ ਵਿੱਚ ਮੌਜੂਦ ਨਹੀਂ ਹਨ।",
    gate_eyebrow:     "ਜੀ ਆਇਆਂ ਨੂੰ",
    gate_title:       "ਆਪਣੀ ਪਸੰਦੀਦਾ ਭਾਸ਼ਾ ਚੁਣੋ",
    gate_copy:        "ਐਪ ਇਸ ਭਾਸ਼ਾ ਵਿੱਚ ਜਵਾਬ ਦੇਵੇਗਾ ਅਤੇ ਆਵਾਜ਼ ਇਨਪੁੱਟ ਲਈ ਇਸਦੀ ਵਰਤੋਂ ਕਰੇਗਾ। ਤੁਸੀਂ ਕਿਸੇ ਵੀ ਸਮੇਂ ਬਦਲ ਸਕਦੇ ਹੋ।",
    error_empty:      "ਪਹਿਲਾਂ ਇੱਕ ਸਵਾਲ ਟਾਈਪ ਕਰੋ।",
    error_voice:      "ਇਸ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਆਵਾਜ਼ ਇਨਪੁੱਟ ਸਮਰਥਿਤ ਨਹੀਂ ਹੈ। Chrome ਜਾਂ Edge ਅਜ਼ਮਾਓ।",
    no_sources:       "ਕੋਈ ਸਰੋਤ ਨਹੀਂ ਮਿਲਿਆ।",
  },
  tamil: {
    app_eyebrow:      "RAG ஒழுங்குமுறை நுண்ணறிவு",
    app_title:        "SEBI மற்றும் RBI சுற்றறிக்கைகள் பற்றி கேளுங்கள்",
    language_trigger: "மொழி",
    checking_index:   "குறியீடு சரிபார்க்கப்படுகிறது",
    question_label:   "கேள்வி",
    voice_btn:        "🎙 குரல்",
    voice_listening:  "🎙 கேட்கிறது…",
    placeholder:      "P2P கடன், கடன் மதிப்பீட்டு நிறுவனங்கள், கடனிலாத்தர் அறங்காவலர், KYC, அனுப்பல் வரம்புகள் பற்றி கேளுங்கள்…",
    domain_label:     "டொமைன்",
    domain_all:       "அனைத்தும்",
    domain_tax:       "வருமான வரி",
    provider_label:   "பதில் வழங்குபவர்",
    sources_only:     "ஆதாரங்கள்",
    topk_label:       "Top K",
    lang_label:       "பதிலின் மொழி",
    ollama_label:     "Ollama மாதிரி",
    openai_label:     "OpenAI மாதிரி",
    hf_label:         "Hugging Face RBI QA சோதனை தரவை சேர்க்கவும்",
    ask_btn:          "கேளுங்கள்",
    ask_working:      "செயல்படுகிறது…",
    sample_btn:       "மாதிரி பயன்படுத்து",
    empty_title:      "ஆதார-ஆதரவு பதிலுக்கு தயார்",
    empty_body:       "ஒரு டொமைனைத் தேர்ந்தெடுங்கள், கேள்வி கேளுங்கள், மேற்கோள் பதிலை உருவாக்குவதற்கு முன் பொருத்தமான பகுதிகளை கணினி தேடும்.",
    loading_title:    "தரவு எடுக்கப்படுகிறது மற்றும் வரைவு தயாரிக்கப்படுகிறது",
    loading_body:     "உள்ளூர் Ollama ஒன்று-இரண்டு நிமிடங்கள் எடுக்கலாம். OpenAI கட்டமைக்கப்பட்டால் வேகமாக இருக்கும்.",
    answer_eyebrow:   "பதில்",
    answer_title:     "உருவாக்கப்பட்ட பதில்",
    sources_eyebrow:  "ஆதாரங்கள்",
    sources_title:    "மீட்டெடுக்கப்பட்ட சூழல்",
    tax_note:         "வருமான வரி ஆவணங்கள் இந்த தொகுப்பில் இன்னும் இல்லை.",
    gate_eyebrow:     "வரவேற்கிறோம்",
    gate_title:       "உங்கள் விருப்பமான மொழியைத் தேர்ந்தெடுங்கள்",
    gate_copy:        "பயன்பாடு இந்த மொழியில் பதிலளிக்கும் மற்றும் குரல் உள்ளீட்டிற்கு பயன்படுத்தும். எப்போது வேண்டுமானாலும் மாற்றலாம்.",
    error_empty:      "முதலில் ஒரு கேள்வியை தட்டச்சு செய்யுங்கள்.",
    error_voice:      "இந்த உலாவியில் குரல் உள்ளீடு ஆதரிக்கப்படவில்லை. Chrome அல்லது Edge முயற்சிக்கவும்.",
    no_sources:       "எந்த ஆதாரமும் கிடைக்கவில்லை.",
  },
  telugu: {
    app_eyebrow:      "RAG నియంత్రణ మేధస్సు",
    app_title:        "SEBI మరియు RBI సర్క్యులర్ల గురించి అడగండి",
    language_trigger: "భాష",
    checking_index:   "సూచిక తనిఖీ అవుతోంది",
    question_label:   "ప్రశ్న",
    voice_btn:        "🎙 వాయిస్",
    voice_listening:  "🎙 వింటోంది…",
    placeholder:      "P2P రుణాలు, క్రెడిట్ రేటింగ్ సంస్థలు, డిబెంచర్ ట్రస్టీలు, KYC, రెమిటెన్స్ పరిమితుల గురించి అడగండి…",
    domain_label:     "డొమైన్",
    domain_all:       "అన్నీ",
    domain_tax:       "ఆదాయపు పన్ను",
    provider_label:   "సమాధాన సదుపాయం",
    sources_only:     "మూలాలు",
    topk_label:       "Top K",
    lang_label:       "సమాధానం భాష",
    ollama_label:     "Ollama మోడల్",
    openai_label:     "OpenAI మోడల్",
    hf_label:         "Hugging Face RBI QA ప్రయోగాత్మక డేటాను చేర్చు",
    ask_btn:          "అడగండి",
    ask_working:      "పని చేస్తోంది…",
    sample_btn:       "నమూనా వాడండి",
    empty_title:      "మూలం-ఆధారిత సమాధానానికి సిద్ధం",
    empty_body:       "డొమైన్ ఎంచుకోండి, ప్రశ్న అడగండి, సిస్టమ్ ఉటంకిత ప్రతిస్పందన ఇవ్వడానికి ముందు సరిపోలే భాగాలను వెతుకుతుంది.",
    loading_title:    "డేటా తీసుకుంటోంది మరియు ముసాయిదా తయారు చేస్తోంది",
    loading_body:     "స్థానిక Ollama ఒకటి-రెండు నిమిషాలు తీసుకోవచ్చు. OpenAI కాన్ఫిగర్ చేస్తే వేగంగా ఉంటుంది.",
    answer_eyebrow:   "సమాధానం",
    answer_title:     "ఉత్పత్తి చేసిన ప్రతిస్పందన",
    sources_eyebrow:  "మూలాలు",
    sources_title:    "తిరిగి పొందిన సందర్భం",
    tax_note:         "ఆదాయపు పన్ను పత్రాలు ఇంకా ఈ సంచికలో లేవు.",
    gate_eyebrow:     "స్వాగతం",
    gate_title:       "మీకు ఇష్టమైన భాషను ఎంచుకోండి",
    gate_copy:        "యాప్ ఈ భాషలో సమాధానం ఇస్తుంది మరియు వాయిస్ ఇన్‌పుట్ కోసం దాన్ని ఉపయోగిస్తుంది. మీరు ఎప్పుడైనా మార్చవచ్చు.",
    error_empty:      "మొదట ఒక ప్రశ్న టైప్ చేయండి.",
    error_voice:      "ఈ బ్రౌజర్‌లో వాయిస్ ఇన్‌పుట్ మద్దతు లేదు. Chrome లేదా Edge ప్రయత్నించండి.",
    no_sources:       "మూలాలు ఏవీ కనుగొనబడలేదు.",
  },
};

function t(key) {
  return (translations[state.language] || translations.english)[key] || translations.english[key] || key;
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.documentElement.lang = languageOptions[state.language]?.speech?.split("-")[0] || "en";
  // keep voice button state correct if listening
  if (voiceButton && voiceButton.classList.contains("listening")) {
    voiceButton.textContent = t("voice_listening");
  }
}

const questionEl = document.querySelector("#question");
const askButton = document.querySelector("#askButton");
const sampleButton = document.querySelector("#sampleButton");
const voiceButton = document.querySelector("#voiceButton");
const topKEl = document.querySelector("#topK");
const ollamaModelEl = document.querySelector("#ollamaModel");
const openaiModelEl = document.querySelector("#openaiModel");
const includeHfEl = document.querySelector("#includeHf");
const emptyState = document.querySelector("#emptyState");
const loadingState = document.querySelector("#loadingState");
const answerCard = document.querySelector("#answerCard");
const answerText = document.querySelector("#answerText");
const providerBadge = document.querySelector("#providerBadge");
const sourcesList = document.querySelector("#sourcesList");
const statusPill = document.querySelector("#statusPill");
const incomeTaxNote = document.querySelector("#incomeTaxNote");
const languageGate = document.querySelector("#languageGate");
const startLanguageGrid = document.querySelector("#startLanguageGrid");
const languageTrigger = document.querySelector("#languageTrigger");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

const samples = [
  { question: "What are the main rules for P2P lending platforms?", domain: "RBI" },
  { question: "What is the rating process for credit rating agencies?", domain: "SEBI" },
  { question: "What are the responsibilities of debenture trustees?", domain: "SEBI" },
];

function setSegment(groupSelector, key, value) {
  document.querySelectorAll(`${groupSelector} .segment, ${groupSelector} .lang-chip`).forEach((button) => {
    button.classList.toggle("active", button.dataset[key] === value);
  });
}

function setLanguage(language) {
  state.language = languageOptions[language] ? language : "english";
  localStorage.setItem("ragPreferredLanguage", state.language);
  setSegment("#languageGroup", "language", state.language);
  applyTranslations();
}

function initializeLanguagePreference() {
  const saved = localStorage.getItem("ragPreferredLanguage");
  if (saved && languageOptions[saved]) {
    state.language = saved;
    setSegment("#languageGroup", "language", state.language);
    applyTranslations();
    languageGate.classList.add("hidden");
  } else {
    languageGate.classList.remove("hidden");
  }
}

function setBusy(isBusy) {
  askButton.disabled = isBusy;
  sampleButton.disabled = isBusy;
  askButton.querySelector("span").textContent = isBusy ? t("ask_working") : t("ask_btn");
  loadingState.classList.toggle("hidden", !isBusy);
  emptyState.classList.add("hidden");
  if (isBusy) answerCard.classList.add("hidden");
}

function showError(message) {
  answerCard.classList.remove("hidden");
  answerText.textContent = message;
  providerBadge.textContent = "Error";
  sourcesList.innerHTML = "";
}

function renderSources(sources) {
  sourcesList.innerHTML = "";
  if (!sources.length) {
    sourcesList.innerHTML = `<div class="source-card"><p class="source-snippet">${t("no_sources")}</p></div>`;
    return;
  }
  for (const source of sources) {
    const card = document.createElement("article");
    card.className = "source-card";
    const isExperimental = source.source_type === "huggingface_dataset_qa";
    const sourceType = isExperimental ? "HF experimental QA" : "Project corpus";
    const url = source.source_url
      ? `<a class="source-link" href="${source.source_url}" target="_blank" rel="noreferrer">Open source</a>`
      : "";
    card.innerHTML = `
      <div class="source-topline">
        <span class="source-label">[${source.label}] ${source.domain}</span>
        <span class="source-score">${source.score}</span>
      </div>
      <div class="source-meta">${source.circular_number}<br>${source.date}</div>
      <span class="source-type ${isExperimental ? "experimental" : ""}">${sourceType}</span>
      <p class="source-snippet">${source.snippet}</p>
      ${url}
    `;
    sourcesList.appendChild(card);
  }
}

async function loadDomains() {
  try {
    const response = await fetch("/domains");
    state.domains = await response.json();
    const available = state.domains
      .filter((d) => d.value !== "all" && d.available)
      .map((d) => `${d.label}: ${d.chunk_count.toLocaleString()}`)
      .join(" | ");
    statusPill.textContent = available || t("checking_index");
    const incomeTax = state.domains.find((d) => d.value === "IncomeTax");
    incomeTaxNote.classList.toggle("hidden", incomeTax?.available);
  } catch {
    statusPill.textContent = "API unavailable";
  }
}

async function askQuestion() {
  const question = questionEl.value.trim();
  if (!question) {
    showError(t("error_empty"));
    return;
  }
  setBusy(true);

  const body = JSON.stringify({
    question,
    domain_filter: state.domain,
    provider: state.provider,
    answer_language: state.language,
    top_k: Number(topKEl.value || 2),
    include_hf_experimental: includeHfEl.checked,
    ollama_model: ollamaModelEl.value.trim() || "qwen2.5-coder:7b",
    openai_model: openaiModelEl.value.trim() || "gpt-4o-mini",
    ollama_timeout: 900,
  });

  try {
    const response = await fetch("/query/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: "Query failed." }));
      throw new Error(err.detail || "Query failed.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let answerAccum = "";
    let sourcesRendered = false;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE lines: "data: {...}\n\n"
      const parts = buffer.split("\n\n");
      buffer = parts.pop(); // keep incomplete tail

      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith("data: ")) continue;
        let event;
        try { event = JSON.parse(line.slice(6)); } catch { continue; }

        if (event.type === "sources") {
          // Sources arrive first — render them immediately
          renderSources(event.sources || []);
          providerBadge.textContent = state.provider;
          sourcesRendered = true;
          // Show answer card with empty text so user knows something is coming
          answerCard.classList.remove("hidden");
          answerText.textContent = "";
          loadingState.classList.add("hidden");
          setBusy(false); // re-enable controls; streaming continues in background
        } else if (event.type === "token") {
          answerAccum += event.token;
          answerText.textContent = answerAccum;
        } else if (event.type === "error") {
          showError(event.message || "An error occurred.");
          break;
        }
        // "done" type: nothing to do
      }
    }
    if (!sourcesRendered) {
      answerCard.classList.remove("hidden");
      answerText.textContent = answerAccum;
    }
  } catch (error) {
    showError(error.message);
    setBusy(false);
    loadingState.classList.add("hidden");
  }
}

function startVoiceInput() {
  if (!SpeechRecognition) {
    showError(t("error_voice"));
    return;
  }
  if (recognition) {
    recognition.stop();
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = languageOptions[state.language]?.speech || "en-IN";
  recognition.interimResults = true;
  recognition.continuous = false;

  let finalTranscript = "";
  voiceButton.classList.add("listening");
  voiceButton.textContent = t("voice_listening");

  recognition.onresult = (event) => {
    let interimTranscript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const tr = event.results[i][0].transcript;
      if (event.results[i].isFinal) finalTranscript += tr;
      else interimTranscript += tr;
    }
    questionEl.value = `${finalTranscript}${interimTranscript}`.trim();
  };

  recognition.onerror = (event) => showError(`Voice input failed: ${event.error}`);

  recognition.onend = () => {
    recognition = null;
    voiceButton.classList.remove("listening");
    voiceButton.textContent = t("voice_btn");
  };

  recognition.start();
}

document.querySelector("#domainGroup").addEventListener("click", (event) => {
  const button = event.target.closest("[data-domain]");
  if (!button || button.classList.contains("unavailable")) return;
  state.domain = button.dataset.domain;
  setSegment("#domainGroup", "domain", state.domain);
});

document.querySelector("#providerGroup").addEventListener("click", (event) => {
  const button = event.target.closest("[data-provider]");
  if (!button) return;
  state.provider = button.dataset.provider;
  setSegment("#providerGroup", "provider", state.provider);
});

document.querySelector("#languageGroup").addEventListener("click", (event) => {
  const button = event.target.closest(".lang-chip, .segment");
  if (!button || !button.dataset.language) return;
  setLanguage(button.dataset.language);
});

askButton.addEventListener("click", askQuestion);
voiceButton.addEventListener("click", startVoiceInput);

startLanguageGrid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-language]");
  if (!button) return;
  setLanguage(button.dataset.language);
  languageGate.classList.add("hidden");
});

languageTrigger.addEventListener("click", () => {
  languageGate.classList.remove("hidden");
});

sampleButton.addEventListener("click", () => {
  const sample = samples[Math.floor(Math.random() * samples.length)];
  questionEl.value = sample.question;
  state.domain = sample.domain;
  setSegment("#domainGroup", "domain", state.domain);
});

questionEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) askQuestion();
});

initializeLanguagePreference();
loadDomains();
