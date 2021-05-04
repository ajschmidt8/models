# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import tensorflow as tf
from merlin_models.tensorflow.layers import DenseFeatures, LinearFeatures


class WideAndDeep(tf.keras.Model):
    """
    https://arxiv.org/pdf/1606.07792.pdf
    """

    def __init__(self, numeric_columns, categorical_columns, **kwargs):
        super(MyModel, self).__init__()
        channels = self.channels(numeric_columns, categorical_columns, **kwargs)

        # Deep channel
        self.deep_input_layer = DenseFeatures(channels["deep"])
        self.deep_final_layer = tf.keras.layers.Dense(1, activation="linear")

        self.deep_hidden_layers = []
        for dim in kwargs["deep_hidden_dims"]:
            self.deep_hidden_layers.append(
                tf.keras.layers.Dense(dim, activation="relu")
            )
            # + batchnorm, dropout, whatever...

        # Wide channel
        self.wide_linear_layer = LinearFeatures(channels["wide"])

        # Channel combiner
        self.combiner_add = tf.keras.layers.Add()
        self.combiner_activation = tf.keras.layers.Activation("sigmoid")

    def channels(self, numeric_columns, categorical_columns, **kwargs):
        """
        Going to just throw everything in both wide and deep channels
        for now. This isn't, in general, how you would want to do this,
        and you may want to do some more complicated logic on the
        ProblemSchema in order to decide how to funnel stuff.
        """
        deep_embedding_dims = kwargs.get("embedding_dims")
        if deep_embedding_dims is None:
            deep_embedding_dims = {
                col.name: kwargs["embedding_dim"] for col in categorical_columns
            }
        deep_embedding_columns = [
            tf.feature_column.embedding_column(col, deep_embedding_dims[col.name])
            for col in categorical_columns
        ]

        return {
            "wide": categorical_columns + numeric_columns,
            "deep": deep_embedding_columns + numeric_columns,
        }

    def call(self, inputs, training=False):
        deep_x = self.deep_input_layer(inputs["deep"])
        for layer in self.deep_hidden_layers:
            deep_x = layer(deep_x)
        deep_x = self.deep_final_layer(deep_x)

        wide_x = self.wide_linear_layer(inputs["wide"])

        combined_x = self.combiner_add([deep_x, wide_x])
        combined_x = self.combiner_activation(combined_x)

        return combined_x
