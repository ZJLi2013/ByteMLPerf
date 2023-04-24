# Copyright 2023 ByteDance and/or its affiliates.
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

import logging
import numpy as np
from byte_mlperf.datasets import test_accuracy
from tqdm import tqdm

log = logging.getLogger("TestAccuracy")


class AccuracyChecker(test_accuracy.AccuracyChecker):
    def calculate_acc(self, data_percent):
        log.info("Start to calculate accuracy...")
        num = int((data_percent / 100) * self.dataloader.get_batch_count()
                  ) if data_percent else self.dataloader.get_batch_count()
        good, total = 0, 0
        diffs = []
        for i in tqdm(range(num)):
            test_data, labels = self.dataloader.get_samples(i)

            results = self.runtime_backend.predict(test_data)
            results = results[list(results)[0]]
            diffs.append(results)

            for j in range(len(results)):
                if np.argmax(results[j].round()) == labels[j].round():
                    good += 1
                total += 1

        accuracy = round((good / total), 5)
        np.save(self.output_dir + "/{}.npy".format(self.dataloader.name()),
                diffs)
        log.info('Batch size is {}, Accuracy: {}'.format(
            self.dataloader.cur_bs, accuracy))
        return {"Top-1": accuracy}
