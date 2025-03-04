import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability FOR A SINGLE PERSON, NOT A GRUOP OF TARGETS.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probabilites = []
    for person in people:
        person_prob = 1
        person_genes = (2 if person in two_genes else 1 if person in one_gene else 0)
        person_trait = person in have_trait
        if person not in one_gene or person not in two_genes:
            # calculating that they have no copies of the gene.
            # if no parents listed, then we use unconditional probability table.
            # each parent passes some number of genes randomly. it can be 0,1,2
            if not people[person]["mother"] is None or not people[person]["father"] is None:
                mother = people[person]["mother"]
                father = people[person]["father"]
                if not mother == None:
                    if mother in one_gene:
                        from_mother = 0.5
                    elif mother in two_genes:
                        from_mother = 1 - PROBS["mutation"]
                    else:
                        from_mother = PROBS["mutation"]

                if not father == None:
                    if father in one_gene:
                        from_father = 0.5
                    elif father in two_genes:
                        from_father = 1 - PROBS["mutation"]
                    else:
                        from_father = PROBS["mutation"]

                if person_genes == 2:
                    person_prob *= from_mother * from_father
                elif person_genes == 1: # we are calucalting the prob that mother or father wont pass a gene because genes == 1
                    person_prob *= (1-from_mother) * from_father + (1-from_father) * from_mother
                else:
                    person_prob *=(1-from_mother)*(1-from_father)

                print(f"Here is the probability of the having gene: {person_prob} * {PROBS['trait'][person_genes][person_trait]}, from {person}")
                probabilites.append(person_prob * PROBS['trait'][person_genes][person_trait])
            
            else:
                person_prob *= PROBS["gene"][person_genes] * PROBS["trait"][person_genes][person_trait]
                
                probabilites.append(person_prob)
    join_prob = 1
    
    for prob in probabilites:
        join_prob *= prob

    
    return join_prob

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p


        if person in have_trait:
            print("has trait " + person)
            probabilities[person]["trait"][True] += p
        elif person not in have_trait:
            probabilities[person]["trait"][False] += p
            


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        # normalizing trait probabilites.
        trait_true = probabilities[person]["trait"][True]
        trait_false = probabilities[person]["trait"][False]
        summary = trait_false + trait_true

        if summary != 1.0:
            #some_value / sum of values. thats how we normalize prob distribution
            probabilities[person]["trait"][True] /= summary
            probabilities[person]["trait"][False] /= summary

        no_genes = probabilities[person]["gene"][0]
        one_gene = probabilities[person]["gene"][1]
        two_genes = probabilities[person]["gene"][2]

        summary_genes = no_genes + one_gene + two_genes

        if summary_genes !=1.0:
            probabilities[person]["gene"][0] /= summary_genes
            probabilities[person]["gene"][1] /= summary_genes
            probabilities[person]["gene"][2] /= summary_genes

            


if __name__ == "__main__":
    main()
