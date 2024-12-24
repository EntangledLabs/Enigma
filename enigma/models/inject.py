from enigma.logger import log

from enigma_models.models.inject import Inject as InjectModel

# Inject
class Inject(InjectModel):

    def __init__(self, id: int, name: str, desc: str, worth: int, path: str | None, rubric: dict):
        super().__init__(id, name, desc, worth, path, rubric)
        self.breakdown = self.calculate_score_breakdown()
        log.debug(f"Created new Inject with name {self.name}")

    def __repr__(self):
        return '<{}> with id {} and name {}'.format(type(self).__name__, self.id, self.name)

    # Calculates the corresponding scores for each scoring category and scoring option
    def calculate_score_breakdown(self):
        log.debug(f"Calculating score breakdown for Inject {self.name}")
        breakdown = dict()
        for key in self.rubric.keys():
            weight = self.worth * self.rubric[key]['weight']
            base_cat_score = weight / (len(self.rubric[key]['categories']) - 1)
            possible_cat_scores = dict()
            for i in range(0, len(self.rubric[key]['categories'].keys())):\
                possible_cat_scores.update({
                    list(self.rubric[key]['categories'].keys())[i]: base_cat_score * i
                })
            breakdown.update({
                key: possible_cat_scores
            })
        return breakdown