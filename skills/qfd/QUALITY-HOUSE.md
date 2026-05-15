# Quality House (TikZ House of Quality)

The QFD matrices in `DESIGN.md` are tables. When a visual rendering is useful — a slide, a doc, a stakeholder review — render the same data as a TikZ "House of Quality" diagram inside a single ` ```tikz ` fence in markdown.

## When to render

Offer this **only when** the cascade has produced enough material to populate it:

- Goals + importance (DESIGN.md §1) and Functions + targets (§2) are filled in, **and**
- The importance matrix (§4) or the roof (§5) — or both — have been resolved.

A house with empty cells is just scaffolding. The point is the populated relation matrix, roof correlations, and basement weights.

## Quick start

Paste the preamble (below) and a `qfdhouse` body inside a single fenced block. An empty body draws the chassis — grid, roof, basement, frame, legend. Once that renders, populate it.

````markdown
```tikz
% --- paste the preamble here ---

\begin{document}
\begin{qfdhouse}
  % WHATs, Importance, HOWs, relations, roof, basement, perception
\end{qfdhouse}
\end{document}
```
````

## Preamble

Paste verbatim before `\begin{document}`:

```tex
% =====================================================================
% QFD "House of Quality" preamble
% =====================================================================
% Usage:
%   \begin{document}
%   \begin{qfdhouse}
%     % WHATs at ({\qfdLeftEdge + 0.1}, {-\r + 0.5})
%     % Importance at ({-\qfdImpW/2}, {-\r + 0.5})
%     % HOWs rotated 90 at ({\c - 0.5}, 0.15)
%     % Relations in cells with [qfdrel/S], [qfdrel/M], [qfdrel/W]
%     % Roof correlations at (C-i-j)
%     % Perception markers at ({\qfdNH + (s+0.5)*\qfdCmpW/6}, {-\r + 0.5})
%     % Basement: target / difficulty / abs weight / rel weight, per HOW
%   \end{qfdhouse}
%   \end{document}
%
% NB: in node text, use $<$ / $>$ for less-than / greater-than under
% OT1 encoding; bare < and > render as Spanish ¡ ¿.
% =====================================================================

\usetikzlibrary{arrows.meta, positioning, shapes.geometric, shapes.misc, calc, fit, backgrounds}

% Toggles — flip before \begin{qfdhouse} to hide sections.
\newif\ifqfdshowroof          \qfdshowrooftrue
\newif\ifqfdshowbasement      \qfdshowbasementtrue
\newif\ifqfdshowcompetitive   \qfdshowcompetitivetrue
\newif\ifqfdshowlegend        \qfdshowlegendtrue
\newif\ifqfdshowimportance    \qfdshowimportancetrue
\newif\ifqfdshowcorrlegend    \qfdshowcorrlegendtrue
\newif\ifqfdshowevallegend    \qfdshowevallegendtrue

% Dimensions — override before \begin{qfdhouse} to resize.
\def\qfdNW{5}           % number of WHATs (rows)
\def\qfdNH{5}           % number of HOWs (columns)
\def\qfdWhatW{4.0}      % width of WHATs column
\def\qfdImpW{0.9}       % width of importance column
\def\qfdCmpW{3}         % width of perception zone
\def\qfdHdrH{2.6}       % height of column-titles band
\def\qfdBasementN{4}    % number of basement rows

% Titles & labels — override before \begin{qfdhouse}.
\def\qfdWhatsTitle{Customer needs}
\def\qfdImpTitle{Imp.\ \%}
\def\qfdPerceptionTitle{Comparative evaluation}
\def\qfdPoorLabel{poor}
\def\qfdExcellentLabel{excellent}
\def\qfdAltOneLabel{Our product}    % highlighted in legend
\def\qfdAltTwoLabel{Competitor A}
\def\qfdAltThreeLabel{Competitor B}
\def\qfdRelTitle{Relation}
\def\qfdCorrTitle{Correlation}
\def\qfdEvalTitle{Evaluation}

% Styles.
\tikzset{
  qfdthin/.style ={line width=0.35pt},
  qfdmed/.style  ={line width=0.7pt},
  qfdstrong/.style={circle, draw, fill=black,
                    minimum size=7pt, inner sep=0pt},
  qfdmod/.style  ={circle, draw,
                    minimum size=7pt, inner sep=0pt, line width=0.8pt},
  qfdweak/.style ={regular polygon, regular polygon sides=3, draw,
                    minimum size=8.5pt, inner sep=0pt, line width=0.7pt},
  qfdrel/.is choice,
  qfdrel/S/.style={qfdstrong},
  qfdrel/M/.style={qfdmod},
  qfdrel/W/.style={qfdweak},
  % Three perception-zone alternatives. Index 1 is emphasised.
  qfdalt1mk/.style={circle, draw, fill=black,
                    minimum size=6pt, inner sep=0pt, line width=1pt},
  qfdalt1ln/.style={line width=1.2pt},
  qfdalt2mk/.style={regular polygon, regular polygon sides=3, draw,
                    fill=black, minimum size=6pt, inner sep=0pt,
                    line width=0.7pt},
  qfdalt2ln/.style={line width=0.7pt, dashed},
  qfdalt3mk/.style={rectangle, draw, fill=black,
                    minimum size=5pt, inner sep=0pt, line width=0.7pt},
  qfdalt3ln/.style={line width=0.7pt, dotted},
}

% --- Grid lines for every zone. ---
\newcommand{\qfdDrawGrid}{%
  \foreach \c in {1,...,\qfdNHm} \draw[qfdthin] (\c, 0) -- (\c, -\qfdNW);
  \foreach \r in {1,...,\qfdNWm} \draw[qfdthin] (0, -\r) -- (\qfdNH, -\r);
  \foreach \r in {1,...,\qfdNWm}
    \draw[qfdthin] (\qfdLeftEdge, -\r) -- (0, -\r);
  \ifqfdshowroof
    \foreach \c in {1,...,\qfdNHm}
      \draw[qfdthin] (\c, 0) -- (\c, \qfdHdrH);
  \fi
  \ifqfdshowcompetitive
    \foreach \r in {1,...,\qfdNWm}
      \draw[qfdthin] (\qfdNH, -\r) -- (\qfdNH+\qfdCmpW, -\r);
  \fi
  \ifqfdshowbasement
    \foreach \r in {1,...,\qfdBasementN}
      \draw[qfdthin] (0, -\qfdNW-\r) -- (\qfdNH, -\qfdNW-\r);
    \foreach \c in {1,...,\qfdNHm}
      \draw[qfdthin] (\c, -\qfdNW) -- (\c, -\qfdNW-\qfdBasementN);
  \fi
}

% --- Roof: diagonal grid + named coordinates (C-i-j) for correlations. ---
\newcommand{\qfdDrawRoof}{%
  \ifqfdshowroof
    \foreach \k in {1,...,\qfdNHm} {%
      \pgfmathsetmacro{\rx}{(\k+\qfdNH)/2}
      \pgfmathsetmacro{\ry}{\qfdHdrH + (\qfdNH-\k)/2}
      \pgfmathsetmacro{\lx}{\k/2}
      \pgfmathsetmacro{\ly}{\qfdHdrH + \k/2}
      \draw[qfdthin] (\k, \qfdHdrH) -- (\rx, \ry);
      \draw[qfdthin] (\k, \qfdHdrH) -- (\lx, \ly);
    }%
    \draw[qfdmed] (0, \qfdHdrH)
       -- (\qfdNH/2, \qfdApexY) -- (\qfdNH, \qfdHdrH);
    \foreach \i in {1,...,\qfdNH}
      \foreach \k in {1,...,\qfdNH} {%
        \pgfmathtruncatemacro{\jj}{\i+\k}
        \ifnum\jj>\qfdNH\relax\else
          \pgfmathsetmacro{\xx}{\i + \k/2 - 0.5}
          \pgfmathsetmacro{\yy}{\qfdHdrH + \k/2}
          \coordinate (C-\i-\jj) at (\xx, \yy);
        \fi
      }%
  \fi
}

% --- Perception scale 0..5 + poor/excellent endpoints + zone title. ---
\newcommand{\qfdDrawScale}{%
  \ifqfdshowcompetitive
    \foreach \tk in {0,1,2,3,4,5} {%
      \pgfmathsetmacro{\tx}{\qfdNH + (\tk+0.5)*\qfdCmpW/6}
      \node[anchor=south, font=\scriptsize] at (\tx, 0.02) {\tk};
    }%
    \node[anchor=south, font=\scriptsize\bfseries, align=center]
         at ({\qfdNH + \qfdCmpW/2}, 0.7) {\qfdPerceptionTitle};
    \node[anchor=north, font=\scriptsize\itshape]
         at ({\qfdNH + 0.45}, -\qfdNW) {\qfdPoorLabel};
    \node[anchor=north, font=\scriptsize\itshape]
         at ({\qfdNH + \qfdCmpW - 0.45}, -\qfdNW) {\qfdExcellentLabel};
  \fi
}

% --- Importance title (left) and WHATs title (header band). ---
\newcommand{\qfdDrawZoneTitles}{%
  \ifqfdshowimportance
    \node[rotate=90, anchor=west, font=\footnotesize\bfseries]
         at ({-\qfdImpW/2}, 0.12) {\qfdImpTitle};
  \fi
  \node[font=\scriptsize\bfseries, align=center, text width=\qfdWhatW cm]
       at ({\qfdLeftEdge + \qfdWhatW/2},
           {\ifqfdshowroof \qfdHdrH/2 \else 0.6 \fi}) {\qfdWhatsTitle};
}

% --- Outer frames around each zone. ---
\newcommand{\qfdDrawFrames}{%
  \begin{scope}[qfdmed]
    \draw (\qfdLeftEdge, 0) rectangle (\qfdNH, -\qfdNW);
    \ifqfdshowimportance \draw (-\qfdImpW, 0) -- (-\qfdImpW, -\qfdNW); \fi
    \draw (0, 0) -- (0, -\qfdNW);
    \ifqfdshowroof
      \draw (0, 0) rectangle (\qfdNH, \qfdHdrH); \fi
    \ifqfdshowbasement
      \draw (0, -\qfdNW) rectangle (\qfdNH, -\qfdNW-\qfdBasementN); \fi
    \ifqfdshowcompetitive
      \draw (\qfdNH, 0) rectangle (\qfdNH+\qfdCmpW, -\qfdNW); \fi
  \end{scope}
}

% --- Legend on the right (Relations / Correlations / Evaluation). ---
\newcommand{\qfdDrawLegend}{%
  \ifqfdshowlegend
    \pgfmathsetmacro{\qfdLegX}{%
      \qfdNH + \ifqfdshowcompetitive \qfdCmpW + 0.7 \else 0.7 \fi}
    \pgfmathsetmacro{\qfdLegBottom}{%
      -2.05
      \ifqfdshowroof    \ifqfdshowcorrlegend - 2.55 \fi \fi
      \ifqfdshowcompetitive \ifqfdshowevallegend - 2.20 \fi \fi}
    \pgfmathsetmacro{\qfdLegY}{\qfdHdrH - 0.4}
    \begin{scope}[shift={(\qfdLegX, \qfdLegY)}]
      \draw[qfdmed, rounded corners=2pt]
        (-0.15, 0.4) rectangle (4.5, \qfdLegBottom);
      % Relations
      \node[anchor=west, font=\footnotesize\bfseries] at (0, 0.1)
        {\qfdRelTitle};
      \draw[qfdthin] (0, -0.15) -- (4.35, -0.15);
      \node[qfdstrong] at (0.22, -0.5)  {};
        \node[anchor=west] at (0.5, -0.5)  {Strong (9)};
      \node[qfdmod]    at (0.22, -0.95) {};
        \node[anchor=west] at (0.5, -0.95) {Medium (3)};
      \node[qfdweak]   at (0.22, -1.4)  {};
        \node[anchor=west] at (0.5, -1.4)  {Weak (1)};
      % Correlations (roof)
      \ifqfdshowroof \ifqfdshowcorrlegend
        \node[anchor=west, font=\footnotesize\bfseries] at (0, -2.10)
          {\qfdCorrTitle};
        \draw[qfdthin] (0, -2.35) -- (4.35, -2.35);
        \node[anchor=west] at (0, -2.70) {{$+\!+$}\quad very positive};
        \node[anchor=west] at (0, -3.05) {{$+$\phantom{$+$}}\quad positive};
        \node[anchor=west] at (0, -3.40) {{$-$\phantom{$-$}}\quad negative};
        \node[anchor=west] at (0, -3.75) {{$-\!-$}\quad very negative};
      \fi \fi
      % Evaluation (3 alternatives)
      \ifqfdshowcompetitive \ifqfdshowevallegend
        \pgfmathsetmacro{\qfdEvalTop}{%
          -2.10 \ifqfdshowroof\ifqfdshowcorrlegend - 2.55 \fi\fi}
        \node[anchor=west, font=\footnotesize\bfseries]
          at (0, \qfdEvalTop) {\qfdEvalTitle};
        \pgfmathsetmacro{\qfdEvalSep}{\qfdEvalTop - 0.25}
        \draw[qfdthin] (0, \qfdEvalSep) -- (4.35, \qfdEvalSep);
        \pgfmathsetmacro{\qfdLegA}{\qfdEvalTop - 0.55}
        \draw[qfdalt1ln] (0.05, \qfdLegA) -- (0.45, \qfdLegA);
          \node[qfdalt1mk] at (0.25, \qfdLegA) {};
          \node[anchor=west, font=\bfseries] at (0.55, \qfdLegA)
            {\qfdAltOneLabel};
        \pgfmathsetmacro{\qfdLegB}{\qfdEvalTop - 0.95}
        \draw[qfdalt2ln] (0.05, \qfdLegB) -- (0.45, \qfdLegB);
          \node[qfdalt2mk] at (0.25, \qfdLegB) {};
          \node[anchor=west] at (0.55, \qfdLegB) {\qfdAltTwoLabel};
        \pgfmathsetmacro{\qfdLegC}{\qfdEvalTop - 1.35}
        \draw[qfdalt3ln] (0.05, \qfdLegC) -- (0.45, \qfdLegC);
          \node[qfdalt3mk] at (0.25, \qfdLegC) {};
          \node[anchor=west] at (0.55, \qfdLegC) {\qfdAltThreeLabel};
      \fi \fi
    \end{scope}
  \fi
}

% --- The environment users wrap their content in. ---
\newenvironment{qfdhouse}{%
  \begin{tikzpicture}[x=1cm, y=1cm, font=\scriptsize,
                      line cap=round, line join=round]
  \ifqfdshowimportance
    \pgfmathsetmacro{\qfdLeftEdge}{-\qfdWhatW-\qfdImpW}
  \else
    \pgfmathsetmacro{\qfdLeftEdge}{-\qfdWhatW}
  \fi
  \pgfmathsetmacro{\qfdApexY}{\qfdHdrH + \qfdNH/2}
  \pgfmathtruncatemacro{\qfdNHm}{\qfdNH - 1}
  \pgfmathtruncatemacro{\qfdNWm}{\qfdNW - 1}
  \qfdDrawGrid
  \qfdDrawRoof
  \qfdDrawScale
  \qfdDrawZoneTitles
}{%
  \qfdDrawFrames
  \qfdDrawLegend
  \end{tikzpicture}%
}
```

## Anatomy

```
                         /\
                        /  \           ← roof: correlations between HOWs
                       /----\
                      /------\
                     /--------\
        ┌──────────────────────┐
        │  HOWs (rotated)      │       ← column titles band
        ├───┬──────────────────┤────────┐
WHATs   │   │                  │        │
labels  │   │   relation       │        │
        │ I │   matrix         │        │ ← perception zone
   +    │ M │                  │        │   0..5 scale
imp.%   │ P │                  │        │
        │   │                  │        │
        ├───┴──────────────────┤
        │     Targets          │
        │     Difficulty       │       ← basement (4 rows per HOW)
        │     Absolute weight  │
        │     Relative weight  │
        └──────────────────────┘
```

| Region                      | Coordinate system                                              |
| --------------------------- | -------------------------------------------------------------- |
| WHATs (left column)         | `({\qfdLeftEdge + 0.1}, {-\r + 0.5})` — row `\r` ∈ 1..`\qfdNW` |
| Importance                  | `({-\qfdImpW/2}, {-\r + 0.5})`                                 |
| HOWs (top, rotated)         | `({\c - 0.5}, 0.15)`, `rotate=90` — column `\c` ∈ 1..`\qfdNH`  |
| Cell (relation)             | `({\c - 0.5}, {-\r + 0.5})`, style `[qfdrel/S\|M\|W]`          |
| Roof correlation            | named coord `(C-i-j)` for HOWs `i` and `j`                     |
| Perception score `s` (0..5) | `({\qfdNH + (s+0.5)*\qfdCmpW/6}, {-\r + 0.5})`                 |
| Basement row 1..4           | `({\c - 0.5}, {-\qfdNW - 0.5})`, `…- 1.5`, `…- 2.5`, `…- 3.5`  |

## Placement recipes

**WHATs + Importance**

```tex
\foreach \r/\t in {1/Easy onboarding, 2/Reliability, 3/Fast UI,
                   4/Affordable,      5/Future-proof}
  \node[anchor=west, font=\scriptsize, text width=\qfdWhatW cm]
    at ({\qfdLeftEdge + 0.1}, {-\r + 0.5}) {\t};

\foreach \r/\imp in {1/25, 2/30, 3/15, 4/20, 5/10}
  \node[font=\scriptsize] at ({-\qfdImpW/2}, {-\r + 0.5}) {\imp};
```

**HOWs (vertical labels)**

```tex
\foreach \c/\t in {1/Bundle size,  2/p95 latency, 3/Error rate,
                   4/Cost/MAU,     5/Test coverage}
  \node[rotate=90, anchor=west, font=\scriptsize]
    at ({\c - 0.5}, 0.15) {\t};
```

**Relations** — pick one of `S` (strong, 9), `M` (medium, 3), `W` (weak, 1):

```tex
\node[qfdrel/S] at ({2 - 0.5}, {-1 + 0.5}) {};  % col 2, row 1
\node[qfdrel/M] at ({4 - 0.5}, {-4 + 0.5}) {};
\node[qfdrel/W] at ({3 - 0.5}, {-3 + 0.5}) {};
```

**Roof correlations** — `(C-i-j)` where `i < j` are HOW column indices:

```tex
\node[font=\scriptsize] at (C-1-2) {$+\!+$};  % very positive
\node[font=\scriptsize] at (C-2-4) {$-$};     % negative
```

**Perception zone** — three alternatives, score per WHAT row:

```tex
\foreach \r/\sone/\stwo/\sthree in
  {1/4/3/2, 2/3/4/3, 3/5/2/3, 4/2/3/4, 5/3/3/2} {
  \pgfmathsetmacro{\xone}{\qfdNH + (\sone + 0.5)*\qfdCmpW/6}
  \pgfmathsetmacro{\xtwo}{\qfdNH + (\stwo + 0.5)*\qfdCmpW/6}
  \pgfmathsetmacro{\xthree}{\qfdNH + (\sthree + 0.5)*\qfdCmpW/6}
  \node[qfdalt1mk] at (\xone,   {-\r + 0.5}) {};
  \node[qfdalt2mk] at (\xtwo,   {-\r + 0.5}) {};
  \node[qfdalt3mk] at (\xthree, {-\r + 0.5}) {};
}
```

**Basement** — per HOW column: target / difficulty (1–5) / absolute weight / relative weight %.

The 4 rows mean, top-to-bottom:

1. **Target** — the spec you commit to (e.g. `<1MB`)
2. **Difficulty** on a 1–5 scale
3. **Absolute weight** = Σ(relation_strength × importance%) over all WHATs that touch this HOW
4. **Relative weight %** = absolute ÷ total absolute. The relative weights across HOWs sum to ~100%, which tells you where the engineering effort should go.

```tex
\foreach \c/\tgt/\diff/\abs/\rel in
  {1/{$<$1MB}/3/120/24,
   2/{$<$200ms}/4/150/30,
   3/{$<$0.1\%}/3/100/20,
   4/{$-$15\%}/2/80/16,
   5/{$>$85\%}/2/50/10} {
  \node[font=\scriptsize] at ({\c - 0.5}, {-\qfdNW - 0.5}) {\tgt};
  \node[font=\scriptsize] at ({\c - 0.5}, {-\qfdNW - 1.5}) {\diff};
  \node[font=\scriptsize] at ({\c - 0.5}, {-\qfdNW - 2.5}) {\abs};
  \node[font=\scriptsize\bfseries] at ({\c - 0.5}, {-\qfdNW - 3.5}) {\rel};
}
```

## Customisation

**Hide sections** — set toggles to `false` *before* `\begin{qfdhouse}`:

```tex
\qfdshowrooffalse           % no correlation triangle
\qfdshowbasementfalse       % no targets/weights below
\qfdshowcompetitivefalse    % no perception zone on the right
\qfdshowlegendfalse         % no side legend
\qfdshowimportancefalse     % no Imp.% column on the left
```

**Resize** — override dimensions *before* `\begin{qfdhouse}`:

```tex
\def\qfdNW{7}        % 7 WHATs instead of 5
\def\qfdNH{6}        % 6 HOWs
\def\qfdWhatW{5.0}   % wider WHATs column for longer labels
```

**Rename labels**:

```tex
\def\qfdWhatsTitle{Besoins client}
\def\qfdImpTitle{Imp.\ \%}
\def\qfdAltOneLabel{Notre produit}
```

## Mapping DESIGN.md → House

| DESIGN.md section          | House region                                            |
| -------------------------- | ------------------------------------------------------- |
| §1 Goals (WHATs)           | left column (WHATs) + Importance                        |
| §2 Functions (HOWs)        | top column titles + basement row 1 (Target)             |
| §4 House matrix (G × F)    | relation cells (`qfdrel/S\|M\|W`)                       |
| §5 Roof (F × F)            | roof correlations at `(C-i-j)`                          |
| §7 Critical perf. budget   | basement rows 2–4 (Difficulty / Abs / Rel weight)       |
| (not in DESIGN.md)         | perception zone — competitive evaluation, optional      |

Skip the perception zone (`\qfdshowcompetitivefalse`) unless a competitor benchmark exists.

## Gotchas

- **`<` and `>` in text mode become `¡` and `¿`.** Use `$<$`, `$>$`, `$-$` or `\textless` / `\textgreater` / `\textendash` inside node text.
- **Only bundled TikZ libraries work.** `arrows.meta`, `positioning`, `shapes.geometric`, `shapes.misc`, `calc`, `fit`, `backgrounds` are in. Arbitrary `\usepackage{…}` is not.
- **No global preamble.** Every diagram has to include the preamble in its own fence today. If you reuse this often, ask for a project-level preamble option.
