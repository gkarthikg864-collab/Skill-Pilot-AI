# 🚀 SkillPilot AI

### Agentic AI-Powered Personalized Learning Platform

SkillPilot AI is an **agentic AI-powered learning platform** designed to provide students with personalized learning support, coding practice, AI-powered quizzes, career guidance, progress tracking, and multiple specialized AI mentors.

The platform is designed around **SDG 4 — Quality Education**, with the goal of making learning more personalized, accessible, interactive, and effective.

---

## 🎯 Problem Statement

Students often use different platforms for learning, coding practice, quizzes, career guidance, and progress tracking.

This creates problems such as:

- Lack of personalized learning paths
- Difficulty identifying what to learn next
- Limited individual guidance
- Separate tools for coding and assessments
- Difficulty tracking learning progress
- Limited career guidance
- Lack of continuous AI-based support

SkillPilot AI brings these learning activities together into one platform.

---

## 💡 Solution

SkillPilot AI acts as a **personalized AI learning companion**.

It combines:

- Personalized learning roadmaps
- AI mentors
- AI quizzes
- Coding practice
- Career guidance
- Progress tracking
- Learning topics and lessons
- Focus timers
- Daily learning streaks
- Multiple programming languages

The platform adapts its guidance based on the student's selected subject, career goal, learning activity, and conversation context.

---

# ✨ Key Features

## 🤖 AI Personal Mentor

A conversational AI mentor that can handle:

- Casual conversations
- Personal learning discussions
- Study motivation
- Stress and study-related concerns
- Daily student conversations
- Context-aware follow-up conversations

The Personal Mentor is designed to respond naturally instead of forcing every conversation into a study plan.

---

## 👨‍🏫 Specialized AI Agents

SkillPilot provides separate AI agents for different purposes:

### Personal Mentor
General personal support and conversation.

### Subject Mentor
Explains programming concepts with examples and practice guidance.

### Code Debugger
Helps identify programming errors and provides corrected solutions.

### Career Mentor
Provides career direction, skills, projects, and interview guidance.

### Study Coach
Helps students create revision strategies and prepare for examinations.

Each agent maintains its own conversation history.

---

# 📚 My Learning

The My Learning section provides a structured learning roadmap.

Each topic can include:

- Definition
- How to use it
- Example
- Key equation or pattern
- Practice task

Students can:

- Open individual learning topics
- Start a focus timer
- Pause the timer
- Reset the timer
- Mark topics as completed
- Practice the selected topic through AI Quiz
- Practice the selected topic through Coding Lab

---

# 📝 AI Quiz

The AI Quiz provides topic-specific questions based on the student's selected learning area.

Features include:

- Multiple-choice questions
- Topic-based questions
- Quiz scoring
- Quiz history
- Accuracy tracking
- Progress integration

---

# 💻 Coding Lab

SkillPilot includes an integrated coding practice environment.

Supported languages include:

- Python
- C
- C++
- Java
- JavaScript

Students can:

1. Read a coding problem
2. Write their solution
3. Provide program input
4. Compile and run the code
5. View the output
6. Fix errors
7. Submit their solution
8. Track coding history

The coding compiler is powered by the local Python backend.

---

# 🎯 Career Coach

The Career Coach connects the student's selected programming subject with possible career paths.

Example:

**Python Programming → AI/ML Engineer**

Possible roadmap:

1. Python
2. NumPy / Pandas
3. Machine Learning
4. Deep Learning
5. RAG / LLM
6. AI Project

Career guidance can include:

- Required skills
- Learning roadmap
- Projects
- Job preparation
- Resume preparation
- Interview preparation

---

# 📊 Progress Tracking

SkillPilot tracks learning activity through:

- Completed learning topics
- Coding submissions
- Quiz performance
- Weekly learning activity
- Learning progress
- Quiz accuracy
- Daily learning streak

This gives students a simple view of their learning progress.

---

# ⏱️ Focus Timer

Each learning topic can have a dedicated focus session.

The timer supports:

- Start
- Pause
- Reset
- Mark topic complete

This encourages students to focus on one learning task at a time.

---

# 🌍 SDG 4 — Quality Education

SkillPilot AI supports:

## Sustainable Development Goal 4: Quality Education

The project aims to contribute to quality education by providing students with:

- Personalized learning support
- Accessible AI assistance
- Interactive learning
- Coding practice
- Continuous feedback
- Career guidance
- Progress tracking

### Goal

> Make high-quality learning more personalized, accessible, and effective through AI.

---

# 🏗️ System Architecture

```text
                 ┌─────────────────────┐
                 │      Student        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   SkillPilot AI     │
                 │     Frontend        │
                 │     index.html      │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       ┌──────────┐   ┌───────────┐   ┌───────────┐
       │ AI       │   │ Coding    │   │ Learning  │
       │ Agents   │   │ Lab       │   │ & Quiz    │
       └────┬─────┘   └─────┬─────┘   └───────────┘
            │               │
            ▼               ▼
      ┌────────────┐   ┌──────────────┐
      │  Ollama    │   │ Python       │
      │  Local AI  │   │ Backend      │
      │ qwen2.5:3b │   │ server.py    │
      └────────────┘   └──────────────┘