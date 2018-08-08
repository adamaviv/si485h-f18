# Course Policy for SI485H Stack Based Binary Exploits (Fall 2018)

## General Information


### Coordinator

-   Asst. Prof. Adam J. Aviv
    -   aviv@usna.edu
    -   MI325
    -   x3-6655


### Course Description

This class covers the foundations of how programs execute on Unix/Linux
machines, to take advantage of vulnerable programs in C and x86 by exploiting
them, and the techniques of those exploits primarily focused on the stack
execution model.


## Course Objectives and Assessment


### Learning Objectives

1.   Understand how programs are loaded and executed in a typical computing environment
2.   The ability to trace and analyze the execution of a program using standard tools (e.g., gdb,strace,ltrace,objdump,readelef)
3.   The ability to identify and exploit vulnerabilities in software
4.   Read, write, and understand x86 assembly programs
5.   Understand system level defenses (e.g., ASLR, stack cannaries) and how to circumvent them
6.   Develop and deploy stack based exploits and shell code (e.g., via stack overflows, format string attacks, ROP)


## Text Book

-   *Hacking: The art of exploitation*, 2nd Edition. Jon Erickson. No Starch
    Press. (**Strongly Recommended**) (*You can probably borrow it from another
    student who is taking Cyber-2*)


## Extra Instruction

-   You are **strongly** encouraged to meet for extra instruction (EI)
    when you are having trouble.
    
-   **The best way to schedule EI is by prior arrangement by email.** This will
    ensure that I'm available and can give you my full attention.

-   I am open to arranging EI via phone/IM/skype etc., but these need to scheduled *a priori*. 

-   You are also welcome to drop by my office anytime to seek unscheduled EI. If I'm
    free, I will be more than happy to work with you.

-   You should always feel free to email me your questions, and I will respond in
    a timely manner. 


## Collaboration Policy

The honor and collaboration policy of this class references and adapts
the language of Computer Science Department Instruction 1531.1D,
[Policy Concerning Programming Projects](http://www.usna.edu/CS/_files/documents/ProgrammingPolicy.pdf). We make the following
course-specific adaptations and revisions below; however, when not
explicitly stated, of the Department's policy holds.


### Homework Collaboration Policy

-   You may work freely with classmates on the homework. This includes working
    together and solving problems together.

-   You are required to indicate all collaborators on your homework assignments.

-   Each student must submit an individual assignment, and the
    pencile-to-paper/fingers-to-keyboard work must be your own. Even when
    collaborating, in many situations, we do not expect two students to produce
    the same answer.

-   Copying of homework assignments is strictly forbidden and is considered an
    honor violation. We define copying as the act of viewing or discussing
    another's answers, copying down those answers without having completed the
    work individually.


### Lab Collaboration Policy

-   You may collaborate on all lab assignments for the purpose of discussion and
    problem exploration; however, each student must individually solve each of
    the lab assignments and submit their own solution.

-   You are **not** allowed to share code or other solution material with others
    (e.g., the secret messages) --- except if you are presenting the lab to the
    class during presentation time.
    
-   You may discuss the main concepts and solution techniques with others and
    collaborate on developing solution processes. Sharing specific solutions,
    however, is strictly against this policy.

-   You are required to indicate all collaborators on your lab assignments via
    an appropriate mechanism (e.g., by submitting a README file). Collaborating
    and not indicating your collaborators is in violation of this and the
    departments policy.


## Classroom Conduct

-   Beverages are permitted in classrooms and labs provided they are in
    closed containers. No food or smokeless tobacco is permitted in
    classrooms or labs.

-   Vulgar language and classroom disruptions will not be tolerated. A
    student who disrupts the class for those reasons will be asked to
    leave immediately and will be marked has having left early in the
    attendance roster and may be considered for a conduct offense.


## Late Policy


### Homework Late Policy

-   Homeworks for each unit will post on the first lecture of that unit and will
    be due on the assigned date for that homework.

-   Homeworks must be submitted in hard copy to the instructor. Late homework
    will not be accepted without prior arrangement from the instructor.


### Lab Late Policy

-   There are no fixed due date for the labs, and you may complete labs at any
    time during the semester, even well after they are assigned.

-   There will be three lab assessment dates at which point your progress will
    be measured and a grade assigned. These will correlate with the 6, 12, and
    16 week grading points.
    



## Grading Policy


### Grading Breakdown


|              | 6-week  | 12-week | 16-Week | Final Grade
|---           |---      |---      |---      |---
| Final Exam   |         |         |         | 20%
| Midterm Exam | 40%     | 40%     | 45%     | 20%
| Practicum    |  8%     |  8%     |  8%     |  8%
| Labs         | 42%     | 42%     | 42%     | 42%
| Homework     | 10%     | 10%     | 10%     | 10%
| **Total**    | **100%**    | **100%**    | **100%**    | **100%**


### Final Exams

-   Final Exams are closed book and closed notes

-   You will be allowed to bring in **one** hand written sheet of paper,
    two sided, with notes on it to be used during the final
    exam. You'll turn in your sheet with your final exam.


### Midterm Exam

-   There are two midterm exams occurring around the X-week.

-   If you are unable to take the midterm, you must provide an
    alternative time to make up the exam to your instructor

-   Midterm exams are closed book and closed notes.

-   You will be allowed to bring in **one** hand written sheet of paper,
    two sided, with notes on it to be used during the exam. You'll turn
    in your sheet with your exam, and will get it back upon grading the
    exam.



### Practicum

-   There will be two practicum exams occuring at the 6 and 12 week
    mark.

-   The practicum will consist of two-to-four short programming
    problems graded on a progressive scale. The scale will be
    announced with the practicum exam.

-   Practicums are designed to test learning and problem solving
    skills in a realistic way, and are thus open notes and open
    Internet. However, you may not communicate with others, in a
    direct fashion (e.g, speaking with a classmate, texting with
    someone outside the classroom, posting on a message board, etc.).


### Labs

-   Each lab will have an assigned point value, between 3 to 5. The point value
    of the lab is relative to the difficulty of the lab. There will be roughly
    100-to-150 or so points assigned via the labs.

-   All labs will be graded using strict PASS/FAIL. No partial credit will
    be provided for lab submission.

-   Your overall lab grade will be graded on a logarithmic scale using the
    following formula.
    
        grade = log(c+1)/log(n+1) 

    where n is the total points assigned, and c is the total points earned by
    completing a lab. 
    
-  Point reductions for labs will occur after each lab assessment date. For
   example, a 3 point following the first lab assessment will only be worth 2
   point, and after the second lab assessment, it will only be worth 1 point,
   and so on. This is to encourage you to submit your labs in a timely manner
   despite the lack of strict deadlines.
   
-  You can receive **lab bonuses** for presenting a lab during presentation
   time. Each lab can only be presented once for a bonus! Each student may only
   present at most 2 times during the semester --- choose your labs wisely!
   
-  To present a lab you must have first submitted and received a correct
   determination from the instructor. The bonus for presenting a lab is 75% of
   the current lab point value (rounded up). This will be added to your c value
   in the above formula. Yes, it is possible to have greater than 100% for your
   lab grade.
   
### Homework

-   Homeworks are roughly assigned for each unit and should be turned in at the
    assigned date, in hard copy.

-   The weight of each homework will be noted on the homework in terms
    of the total points available for that homework.

### Merge Request Bonus and Bug/Content Bounty Bonus

-   You can receive up to a 5% bonus on *your final grade* for submitting useful
    merge requests (sometimes called pull requests) to the course. The value of the merge requests
    are limmitted in terms of total bonus points awarded per catagory and the number of available points 
    overall (limmited to 5% total bonus); however, exceptions may be made in exceptional circumstances due to
    exceptional contributions at the discretion of the instructor.
    
-   Merge requests for typos in the unit notes are worth 0.05 points each, on
    your final grade. Your merge requests must be in the same style as the document. 
    You can only receive up to 1% points for typo corrections on your final grade. 

-   Merge request for new or corrected content in the unit notes (due to errors
    or out-of-date) can be worth as much as 0.5% points, or more, depending on the
    quality of the corrections. The quality of the correction is at the
    discretion of the instructor and must be more than just typo corrections. You
    can receive up to 1.5% points for error/out-of-date corrections. 
    
-   Merge requests that include new content beyond the unit are also encouraged
    and can be worth as much as 1% points, depending on length and depth
    of the content, and should be placed in the `extra` folder in the course
    repository. The exact value is at the discretion of the instructor. You can
    receive up to 2% points for new content. 

-   Bonuses are also available for creating new labs and problems. These can
    earn up to a 1 point bonus, depending on the difficulty and creativity of
    the lab. These should be submitted to the instructor as a separate repository,
    and the intention should be disc cussed with the instructor prior to
    submission so that the lab can be deployed for other students to enjoy. You
    can receive up to 2% points for new, deployed labs.

-   When providing new content, you must cite appropriate sources, and the
    writing should be your own. The honor code holds.
    

<hr>
<b> APPROVED </b><br><br>
<br>
<br>

<div style="float:left;margin-left:25px">
___________________<br>
Adam J. Aviv <br> 
Course Coordinator <br>
</div>


<div style="float:left;margin-left:100px">
___________________ <br>
CAPT Michael Bilzor<br>
CS Department Chair <br>
</div>

<br>
<br>
<br>

