"""
source: https://levelup.gitconnected.com/10-interesting-python-programs-with-code-b676181a2d1a
source of the text is from WIKIPEDIA about Shakespeare's life: https://en.wikipedia.org/wiki/Shakespeare%27s_plays

The output is PNG file format; however, Windows PC is unable to recognize the output PNG file. The file is probably
not generated correctly
"""
import pywhatkit

text = "As was common in the period, Shakespeare based many of his plays on the work of other playwrights and " \
       "recycled older stories and historical material. His dependence on earlier sources was a natural consequence " \
       "of the speed at which playwrights of his era wrote; in addition, plays based on already popular stories " \
       "appear to have been seen as more likely to draw large crowds. There were also aesthetic reasons: Renaissance " \
       "aesthetic theory took seriously the dictum that tragic plots should be grounded in history. For example, " \
       "King Lear is probably an adaptation of an older play, King Leir, and the Henriad probably derived from The " \
       "Famous Victories of Henry V.[28] There is speculation that Hamlet (c. 1601) may be a reworking of an older, " \
       "lost play (the so-called Ur-Hamlet),[29] but the number of lost plays from this time period makes it " \
       "impossible to determine that relationship with certainty. (The Ur-Hamlet may in fact have been Shakespeare's, " \
       "and was just an earlier and subsequently discarded version.)[28] For plays on historical subjects, Shakespeare " \
       "relied heavily on two principal texts. Most of the Roman and Greek plays are based on Plutarch's Parallel " \
       "Lives (from the 1579 English translation by Sir Thomas North),[30] and the English history plays are indebted " \
       "to Raphael Holinshed's 1587 Chronicles. This structure did not apply to comedy, and those of Shakespeare's " \
       "plays for which no clear source has been established, such as Love's Labour's Lost and The Tempest, are " \
       "comedies. Even these plays, however, rely heavily on generic commonplaces. While there is much dispute about " \
       "the exact chronology of Shakespeare's plays, the plays tend to fall into three main stylistic groupings. " \
       "The first major grouping of his plays begins with his histories and comedies of the 1590s. Shakespeare's " \
       "earliest plays tended to be adaptations of other playwrights' works and employed blank verse and little " \
       "variation in rhythm. However, after the plague forced Shakespeare and his company of actors to leave London " \
       "for periods between 1592 and 1594, Shakespeare began to use rhymed couplets in his plays, along with more " \
       "dramatic dialogue. These elements showed up in The Taming of the Shrew and A Midsummer Night's Dream. " \
       "Almost all of the plays written after the plague hit London are comedies, perhaps reflecting the public's " \
       "desire at the time for light-hearted fare. Other comedies from Shakespeare during this period include Much " \
       "Ado About Nothing, The Merry Wives of Windsor and As You Like It. The middle grouping of Shakespeare's " \
       "plays begins in 1599 with Julius Caesar. For the next few years, Shakespeare would produce his most famous " \
       "dramas, including Macbeth, Hamlet, and King Lear. The plays during this period are in many ways the darkest " \
       "of Shakespeare's career and address issues such as betrayal, murder, lust, power and egoism. The final " \
       "grouping of plays, called Shakespeare's late romances, include Pericles, Prince of Tyre, Cymbeline, The " \
       "Winter's Tale and The Tempest. The romances are so called because they bear similarities to medieval romance " \
       "literature. Among the features of these plays are a redemptive plotline with a happy ending, and magic and " \
       "other fantastic elements."


if __name__ == '__main__':
    pywhatkit.text_to_handwriting(text)
