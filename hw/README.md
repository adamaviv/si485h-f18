# Homework


## Instructions

You must submit HW printed out using the latex templates provided in the
[template](hw/templates) folder, but you can purruse the hw in markdown above. The
due date of the homework is posted on the [calendar](calendar.md).

## Latex Answer Environment

There is an `myanswer` environment defined in the latex template that you should
use for formatting your answer. For example, if had the following question, the
answer would appear like so.

```{.latex}
\item What is the meaning of life, universe, everything?
\being{myanswer}
    The answer is 42!
\end{myanswer}
```

You can use other format environments within a `myanswer` environment, such as
`verbatim` or `lstlisting`. This is useful when you want specific formatting to
occur.

Critically, you MUST format your HW properly such that each answer can be
properly graded. Bad latex formatting is not an excuse for a poor submissions.

## Compiling Latex 

### On Ubuntu

You can install your own latex environment on your Ubuntu VM via `apt-get`

```
sudo apt-get instal texlive-full
```

This will install a lot of stuff! But, once finished, you can compile using
`pdflatex`, like so. 

```
pdflatex hw_05.tex
```

This will produce a bunch of extra files, like an `aux` file, which you can
ignore, but it will also produce a pdf file, `hw_05.pdf`.

### On Overleaf

Check out [Overleaf](https://overleaf.com) as way to compile latex in the
browser. You'll need to create a project and upload the template. You can
compile and compose online, and download/print the resulting pdf file.






