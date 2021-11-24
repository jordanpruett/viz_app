# viz_app
Dash app for exploring results of a text classification project on the US Novel Corpus 1880-2000 for the Textual Optics Lab. Full texts of 9,089 novels were represented as TF-IDF vectors, then those with a Library of Congress genre tag were used as training data to predict the genre of those without a tag. Classification used logistic regression on the top 10,000 words by document frequency. 

The app displays genre predictions for each novel, confidence scores for predictions, and a t-SNE projection of the underlying TF-IDF features, colored by Library of Congress genre.

You can read a blog post about the project [here](https://textual-optics-lab.blogspot.com/2020/07/machine-learning-for-genre.html).

And you can see the app in action at [this link](https://classifier-viz-app.herokuapp.com/). 

# Components

## Search By Author
This lets you search by author names to explore which authors and titles are contained in the corpus. For each author, it lists the title of each of their books in the corpus, that book’s publication date, and the predicted genre of that book. Note that the search function is very bare-bones; you’ll need to search by exact match.

## Genre Confidence
For each title in the corpus, this component shows the confidence score associated with each of that title’s genre predictions. A value higher than 0.5 resulted in a positive prediction for that genre, but it can also be interesting to see just how confident the classifier was in the prediction.

## Top Words for Each Genre
This component lists the top model features for each genre. These are the words that have the highest and lowest assigned coefficients in the model. Out of the 10,000 words in the prediction vocabulary, they have the highest or lowest prediction weights. Most of them are quite intuitive: the top word for detective and mystery ficiton is, unsurprisingly, “detective.” The most amusing are the words that are negatively associated with religious fiction: damn, shit, hell, bastard, brandy, ass. Sounds like a boring genre!

## 2-D Projection of the Feature Space
Lastly, the app lets you explore a 2-D t-SNE projection of the ~9,000 novels, colored by genre, in the feature space. The underlying features of the data are tf-idf scores for the top 10,000 most-used words in the whole corpus. Treating each word-count as a dimension, this projection basically shows you which novels are close together in that 10,000-dimensional space. The projection largely agrees with the classifier, as we can see at first glance. But be wary: t-SNE preserves the local (but not global) structure of your data. So only the clusters are meaningful, not the relative distance of several clusters from each other. You can mouse over a point to see which novel it is.
