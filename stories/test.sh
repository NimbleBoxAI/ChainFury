echo "######\n>      python3 -m stories.fury_form\n######" && python3 -m stories.fury_form

echo "######\n>      python3 -m stories.fury_core nodes callm\n######" && python3 -m stories.fury_core nodes callm
echo "######\n>      python3 -m stories.fury_core nodes callai\n######" && python3 -m stories.fury_core nodes callai
echo "######\n>      python3 -m stories.fury_core nodes callai\n######" && python3 -m stories.fury_core nodes callai --jtype
echo "######\n>      python3 -m stories.fury_core nodes callai_chat\n######" && python3 -m stories.fury_core nodes callai_chat
echo "######\n>      python3 -m stories.fury_core nodes callai_chat\n######" && python3 -m stories.fury_core nodes callai_chat --jtype

QUOTE="to great men and women who defined a new era for humanity!"

echo "######\n>      python3 -m stories.fury_core chain callpp\n######" && python3 -m stories.fury_core chain callpp
echo "######\n>      python3 -m stories.fury_core chain callpj\n######" && python3 -m stories.fury_core chain callpj
echo "######\n>      python3 -m stories.fury_core chain calljj\n######" && python3 -m stories.fury_core chain calljj
echo "######\n>      python3 -m stories.fury_core chain callj3\n######" && python3 -m stories.fury_core chain callj3 --quote "$QUOTE"

SCENE="ufo attacked a crow and stole 5 year olds ice cream"
TOPICS='dolphins, redbull, 5 year old'

echo "######\n>      python3 -m stories.fury_algo algo io\n######" && python3 -m stories.fury_algo algo io "$SCENE"
echo "######\n>      python3 -m stories.fury_algo algo cot\n######" && python3 -m stories.fury_algo algo cot "$SCENE"
echo "######\n>      python3 -m stories.fury_algo algo cot_t\n######" && python3 -m stories.fury_algo algo cot_t "$TOPICS"
echo "######\n>      python3 -m stories.fury_algo algo cot-sc\n######" && python3 -m stories.fury_algo algo cot-sc "$SCENE" --n 3
echo "######\n>      python3 -m stories.fury_algo algo tot\n######" && python3 -m stories.fury_algo algo tot "$TOPICS" --max_search_space 2
