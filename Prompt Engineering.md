 ####  Element of a prompt
 - [x] Input/Context
 - [x] Instruction
 - [x] Questions
 - [x] Examples
 - [x] Output format
 - [x] Constraint 

#### Some Hacks
- Let the model say "I don't know" to prevent hallucinations
- Give the model room to "think" before responding
- Break complex tasks into subtasks
- Check the model's comprehension

#### Iterating Tips
- Try to use different prompts to find what works best(**few-shot**、**Chain-of-Thought**、**Tree-of-Thought**、 **Self-consistency**、**Prompt Chaining**)
- When attempting few-shot learning, try also including direct instructions
- Rephrase a direct instruction set to be more or less concise, e.g. taking a previous example of just saying "Translate." and expanding on the instruction to say "Translate from English to Spanish."
- Try different **personal** keywords to see how it affects the response style
- Use fewer or more examples in your few-shot learning
- Prompt chaining is a technique where we try to achieve a complex task by breaking it down into smaller sequential prompt
- 

#### Reference
- [Understanding Prompt Engineering: A Comprehensive 2024 Survey](https://medium.com/@elniak/understanding-prompt-engineering-a-comprehensive-2024-survey-4ecea29694ce)
- [火山引擎豆包模型Prompt最佳实践](https://www.volcengine.com/docs/82379/1221660)
- [How Tree of Thoughts Prompting Works](https://medium.com/@dan_43009/how-tree-of-thoughts-prompting-works-54dbd9650ad3)
- [Prompt Hub](https://app.prompthub.us/login)

