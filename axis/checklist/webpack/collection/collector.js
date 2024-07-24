import { DjangoInputCollection } from 'input-collection-api';

class Collector {
    constructor() {
        this.reset();
    }

    reset() {
        this.collectors = {};
        this.collector = null;
        this.api = null;
        this.instruments = {};
    }
    initialize(collectionInfo, keepPrevious) {
        if (!keepPrevious) {
            this.reset();
        }

        let specification = collectionInfo.specification;

        let obj = DjangoInputCollection(specification.meta.api);
        obj.full_specification = specification;
        obj.instruments = collectionInfo.instruments;

        this.collectors[specification.collection_request.id] = Object.assign({}, obj);
        this.collectors[specification.eep_program_id] = Object.assign({}, obj);

        // Courtesy initialization for working with just one object at a time
        if (this.collectors.length === 1) {
            this.setCollector(id);
        }
    }
    setCollector(id) {
        this.collector = this.collectors[id] || null;
        this.api = this.collector.api;
        this.instruments = this.collector.instruments;
    }
}

export const collector = new Collector();
