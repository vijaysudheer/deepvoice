import numpy as np

from keras.models import Sequential, Model
from keras.layers import Activation, TimeDistributed, Bidirectional, LSTM, GRU, Dense, InputLayer, RepeatVector, Input
from keras.optimizers import Nadam
from keras.utils.visualize_util import plot

from recurrentshop.engine import RecurrentContainer
from recurrentshop.cells import GRUCell, LSTMCell

from deepvoice.data.cmudict import get_cmudict, test_dataset_cmudict
from deepvoice.util.util import sparse_labels

def G2P(layers, batch=32, chars=29, phons=75, word_len=28, phon_len=28, tables=None, build=True):
    """
    Grapheme-to-phoneme converter; RNN GRU encoder-decoder model.
    # Arguments
        layers: Amount of layers for the encoder and decoder.
        batch: The batch size.
        chars: The amount of characters (English has 29).
        phons: The amount of phonemes (CMUDict uses 75).
        word_len: The length of the input word (CMUDict uses 28).
        phon_len: The length of the output phoneme (CMUDict uses 28).
        tables: Charecter en/decoding tables, can be retrieved by `get_cmudict()`.
        build: If to compile the model in Keras (the model will expect sprase labels).

    # Output
        A Keras model.
        Input:  `(word_length, chars)` shaped one-hot vectors.
        Output: `(word_length, phons)` shaped one-hot vectors.

    # Example
        ```
        (X_train, y_train), (X_test, y_test), (xtable, ytable) = get_cmudict()
        y_train = sparse_labels(y_train)

        model = G2P(layers=3, batch=1024, tables=(xtable, ytable))
        model.fit(X_train, y_train, batch_size=1024, nb_epoch=20)
        ```
    """

    # Decode data into neat named variables.
    if tables is not None:
        chars = len(tables[0].chars)
        phons = len(tables[1].chars)
        word_length = tables[0].maxlen
        phon_length = tables[1].maxlen

    # Define our model's input.
    input_seq = Input(batch_shape=(batch, word_length, chars))



    # Finalize the model.
    model = Model([input_seq, ground_truth], output_softmax)

    if build:
        model.compile(loss='sparse_categorical_crossentropy',
                      optimizer=Nadam(),
                      metrics=['accuracy'])

    return model

def test_fit_G2P():
    # Test CMUDict.
    test_dataset_cmudict()

    # Get CMUDict data.
    (X_train, y_train), (_, _), (xtable, ytable) = get_cmudict(
        verbose=1,
        test_size=0.
    )

    # Sparse labels.
    sparse_y_train = sparse_labels(y_train)

    # Define model.
    batch = 1024
    model = G2P(layers=3, batch=batch, tables=(xtable, ytable))

    # Summerize and plot model.
    model.summary()
    plot(model)

    # Crop the training data so it fits the batch size.
    X_batched = X_train[:X_train.shape[0]//batch*batch]
    y_batched = y_train[:y_train.shape[0]//batch*batch]

    y_sparse_batched = sparse_y_train[:sparse_y_train.shape[0]//batch*batch]

    # Fit the model.
    model.fit([X_batched, y_batched], y_sparse_batched, batch_size=batch, nb_epoch=1, verbose=1)

if __name__ == "__main__":
    test_fit_G2P()
